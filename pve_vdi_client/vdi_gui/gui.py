import os
import sys
import traceback

from configparser import RawConfigParser
from proxmoxer.backends.https import AuthenticationError
from PySide2.QtWidgets import (QApplication, QPushButton, QComboBox, QCheckBox, 
                               QDialog, QDialogButtonBox, QGroupBox,
                               QFormLayout, QMessageBox, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout)

from pve_vdi_client import CLIENT_PATHS
from pve_vdi_client.vdi_client.client import Client

class Gui(QDialog):
  def __init__(self):
    super().__init__()

    self.config = RawConfigParser()
    self.config.read(CLIENT_PATHS)

    self._server_input = QLineEdit()
    self._server_input.setFixedWidth(250)
    self._server_input.setText(self.config['client'].get('server', None))

    self._user_input = QLineEdit()
    self._user_input.setFixedWidth(250)
    self._user_input.setText(self.config['client'].get('username', None))

    password_box = QLineEdit()
    password_box.setFixedWidth(250)
    password_box.setEchoMode(QLineEdit.Password)
    password_box.setText(self.config['client'].get('password', None))
    self._password_input = password_box

    self._verify_ssl_checkbox = QCheckBox("Verify SSL")
    self._verify_ssl_checkbox.setChecked(self.config['client'].getboolean('verify_ssl', True))
    self._filter_checkbox = QCheckBox("SPICE-capable only (slow!)")
    self._filter_checkbox.setChecked(self.config['gui'].getboolean('spice_filter', False))

    self._fetch_button = QPushButton()
    self._update_fetch_button_to_default()
    self._fetch_button.pressed.connect(self._update_fetch_button_to_loading)
    self._fetch_button.clicked.connect(self._set_client_and_fetch_vms)
    self._fetch_button.released.connect(self._update_fetch_button_to_default)

    self._vm_dropdown = QComboBox()
    self._vm_dropdown.setDisabled(True)
    self._vm_dropdown.setFixedWidth(300)
    self._vm_dropdown.currentTextChanged.connect(self._toggle_favorites_button_text)

    self._favorites_button = QPushButton()
    self._favorites_button.setText("Favorite")
    self._favorites_button.clicked.connect(self._toggle_vm_to_favorites)

    self._authentication_message_box = QMessageBox()

    self._client = None

    self._okay_button = QDialogButtonBox.Ok

    button_box = QDialogButtonBox(self._okay_button | QDialogButtonBox.Cancel)

    button_box.accepted.connect(self._connect_to_vm)
    button_box.rejected.connect(self.reject)

    main_layout = QVBoxLayout()
    main_layout.setStretch(0, 2)
    main_layout.addWidget(self.horizontal_credentials_element())
    main_layout.addWidget(self.vm_list_element())
    main_layout.addWidget(button_box)
    self.setLayout(main_layout)

    self.setWindowTitle("PVE VDI Client")

  def horizontal_credentials_element(self):
    _horizontal_group_box = QGroupBox("Credentials")
    layout = QFormLayout()
    layout.addRow(QLabel("Server: "), self._server_input)
    layout.addRow(QLabel("Username:"), self._user_input)
    layout.addRow(QLabel("Password:"), self._password_input)
    layout.addRow(self._verify_ssl_checkbox)
    layout.addRow(self._filter_checkbox)
    layout.addRow(self._fetch_button)

    _horizontal_group_box.setLayout(layout)
    return _horizontal_group_box

  def vm_list_element(self):
    _horizontal_group_box = QGroupBox("VMs")
    form_layout = QFormLayout()
    selection_layout = QFormLayout()
    selection_layout.addRow(self._vm_dropdown, self._favorites_button)
    form_layout.addRow(QLabel("VM: "), selection_layout)

    _horizontal_group_box.setLayout(form_layout)
    return _horizontal_group_box

  def show_message_box(self, text=None, informative_text=None):
    if text:
      self._authentication_message_box.setText(text)
    if informative_text:
      self._authentication_message_box.setInformativeText(informative_text)
    self._authentication_message_box.exec()

  def favorites_section_name(self):
    return "favorites:{}".format(self._server_input.text())

  def _toggle_vm_to_favorites(self):
    favorites = self._get_favorites()
    favorite_name = self._vm_dropdown.currentText()
    if self._favorites_button.text() == "Favorite":
      favorites.append(favorite_name)
    if self._favorites_button.text() == "Unfavorite":
      favorites.remove(favorite_name)
    self.config.set(self.favorites_section_name(), 'favorites', ",".join(filter(lambda x: x != "", favorites)))
    self._save_config()
    self._fetch_vms()
    self._vm_dropdown.setCurrentIndex(self._vm_dropdown.findText(favorite_name))

  def _get_favorites(self):
    if self.favorites_section_name() not in self.config.sections():
      self.config.add_section(self.favorites_section_name())
      self.config.set('favorites', '')
    return self.config.get(self.favorites_section_name(), 'favorites').split(",")

  def _fetch_vms(self):
    if self._filter_checkbox.isChecked():
      vms = self._client.get_vms(include_config=True, vga=r"qxl.*")
    else:
      vms = self._client.get_vms()
    self._vm_dropdown.clear()
    found_favorites = []
    vms = ["{}-{}".format(vm['vmid'], vm['name']) for vm in vms]
    for idx, vm in enumerate(vms):
      if vm in self._get_favorites():
        found_favorites.append(vms.pop(idx))
    if found_favorites:
      self._vm_dropdown.addItems(sorted(found_favorites))
      self._vm_dropdown.insertSeparator(len(found_favorites))
    self._vm_dropdown.addItems(sorted(vms))
    self._vm_dropdown.setEnabled(True)
    self._save_config()

  def _update_fetch_button_to_loading(self):
    self._fetch_button.setText("Loading...")

  def _update_fetch_button_to_default(self):
    self._fetch_button.setText("Fetch VMs")

  def _set_client_and_fetch_vms(self):
    try:
      self._client = Client(host=self._server_input.text(),
                            user=self._user_input.text(),
                            password=self._password_input.text())
      self._fetch_vms()
    except AuthenticationError as e:
      traceback.print_exc()
      self.show_message_box(text="Authentication Error!", informative_text=repr(e))
    except Exception as e:
      traceback.print_exc()
      self.show_message_box(text="Unhandled Error!", informative_text=repr(e))
    finally:
      self._update_fetch_button_to_default()
    return None

  def _connect_to_vm(self):
    vm_id = int(self._vm_dropdown.currentText().split("-")[0])
    self._client.spice_connect(
      remote_viewer_bin_path=self.config['client'].get('remote_viewer_path', 'remote-viewer'), 
      vmid=vm_id
    )

  def _save_config(self):
    self.config.set('client', 'server', self._server_input.text())
    self.config.set('client', 'username', self._user_input.text())
    self.config.set('client', 'password', self._password_input.text())
    self.config.set('client', 'verify_ssl', self._verify_ssl_checkbox.isChecked())
    self.config.set('gui', 'spice_filter', self._filter_checkbox.isChecked())
    for conffile in CLIENT_PATHS:
      if os.path.exists(conffile):
        with open(conffile, 'w') as configfile:
          self.config.write(configfile)

  def _toggle_favorites_button_text(self):
    if self._vm_dropdown.currentText() in self._get_favorites():
      self._favorites_button.setText("Unfavorite")
    else:
      self._favorites_button.setText("Favorite")


def run():
  app = QApplication(sys.argv)
  gui = Gui()
  sys.exit(gui.exec())

if __name__ == '__main__':
  run()