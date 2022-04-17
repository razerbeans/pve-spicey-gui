"""PySide6 port of the widgets/layouts/basiclayout example from Qt v5.x"""

import os
import sys

from pve_vdi_client import CLIENT_PATHS

from configparser import RawConfigParser
from proxmoxer.backends.https import AuthenticationError
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QApplication, QPushButton, QComboBox, QCheckBox, 
                               QDialog, QDialogButtonBox, QGridLayout, QGroupBox,
                               QFormLayout, QMessageBox, QLabel, QLineEdit,
                               QMenu, QMenuBar, QPushButton, QSpinBox,
                               QTextEdit, QVBoxLayout, QWidget)

from ..vdi_client.client import Client

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
    self._update_button_to_default()
    self._fetch_button.pressed.connect(self._update_button_to_loading)
    self._fetch_button.clicked.connect(self._set_client_and_fetch_vms)
    self._fetch_button.released.connect(self._update_button_to_default)

    self._vm_dropdown = QComboBox()
    self._vm_dropdown.setDisabled(True)
    self._vm_dropdown.setFixedWidth(300)

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
    layout = QFormLayout()
    layout.addRow(QLabel("VM: "), self._vm_dropdown)

    _horizontal_group_box.setLayout(layout)
    return _horizontal_group_box

  def show_message_box(self, text=None, informative_text=None):
    if text:
      self._authentication_message_box.setText(text)
    if informative_text:
      self._authentication_message_box.setInformativeText(informative_text)
    self._authentication_message_box.exec()

  def _fetch_vms(self):
    if self._filter_checkbox.isChecked():
      vms = self._client.get_vms(include_config=True, vga=r"qxl.*")
    else:
      vms = self._client.get_vms()
    self._vm_dropdown.clear()
    self._vm_dropdown.addItems(sorted(["{}-{}".format(vm['vmid'], vm['name']) for vm in vms]))
    self._vm_dropdown.setEnabled(True)
    self._write_config()

  def _update_button_to_loading(self):
    self._fetch_button.setText("Loading...")

  def _update_button_to_default(self):
    self._fetch_button.setText("Fetch VMs")

  def _set_client_and_fetch_vms(self):
    try:
      self._client = Client(host=self._server_input.text(),
                            user=self._user_input.text(),
                            password=self._password_input.text())
      self._fetch_vms()
    except AuthenticationError as e:
      self.show_message_box(text="Authentication Error!", informative_text=repr(e))
    except Exception as e:
      self.show_message_box(text="Unhandled Error!", informative_text=repr(e))
    finally:
      self._update_button_to_default()
    return None

  def _connect_to_vm(self):
    vm_id = int(self._vm_dropdown.currentText().split("-")[0])
    self._client.spice_connect(
      remote_viewer_bin_path=self.config['client'].get('remote_viewer_path', 'remote-viewer'), 
      vmid=vm_id
    )

  def _write_config(self):
    self.config.set('client', 'server', self._server_input.text())
    self.config.set('client', 'username', self._user_input.text())
    self.config.set('client', 'password', self._password_input.text())
    self.config.set('client', 'verify_ssl', self._verify_ssl_checkbox.isChecked())
    self.config.set('gui', 'spice_filter', self._filter_checkbox.isChecked())
    for conffile in CLIENT_PATHS:
      if os.path.exists(conffile):
        with open(conffile, 'w') as configfile:
          self.config.write(configfile)


def run():
  app = QApplication(sys.argv)
  gui = Gui()
  sys.exit(gui.exec())

if __name__ == '__main__':
  run()