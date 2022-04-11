"""PySide6 port of the widgets/layouts/basiclayout example from Qt v5.x"""

import sys

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QApplication, QPushButton, QComboBox, QDialog,
                               QDialogButtonBox, QGridLayout, QGroupBox,
                               QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QMenu, QMenuBar, QPushButton, QSpinBox,
                               QTextEdit, QVBoxLayout, QWidget)

from ..vdi_client.client import Client

class Gui(QDialog):
  def __init__(self):
    super().__init__()

    self._server_input = QLineEdit()
    self._user_input = QLineEdit()
    password_box = QLineEdit()
    password_box.setEchoMode(QLineEdit.Password)
    self._password_input = password_box
    
    self._fetch_button = QPushButton("Fetch VMs")
    self._fetch_button.clicked.connect(self._set_client)

    self._vm_dropdown = QComboBox()
    self._vm_dropdown.setDisabled(True)
    self._vm_dropdown.setFixedWidth(300)
    
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

    self.setWindowTitle("Basic Layouts")

  def horizontal_credentials_element(self):
    _horizontal_group_box = QGroupBox("Credentials")
    layout = QFormLayout()
    layout.addRow(QLabel("Server: "), self._server_input)
    layout.addRow(QLabel("User:"), self._user_input)
    layout.addRow(QLabel("Password:"), self._password_input)
    layout.addRow(self._fetch_button)

    _horizontal_group_box.setLayout(layout)
    return _horizontal_group_box

  def vm_list_element(self):
    _horizontal_group_box = QGroupBox("VMs")
    layout = QFormLayout()
    layout.addRow(QLabel("VM: "), self._vm_dropdown)

    _horizontal_group_box.setLayout(layout)
    return _horizontal_group_box


  def _fetch_vms(self):
    vms = self._client.cluster_vms()
    self._vm_dropdown.addItems(sorted(["{}-{}".format(vm['vmid'], vm['name']) for vm in vms]))
    self._vm_dropdown.setEnabled(True)
    self.button_box.accepted.setEnabled(True)

  def _set_client(self):
    self._client = Client(host=self._server_input.text(),
                          user=self._user_input.text(),
                          password=self._password_input.text())
    self._fetch_vms()
    return None

  def _connect_to_vm(self):
    vm_id = int(self._vm_dropdown.currentText().split("-")[0])
    self._client.spice_connect(vmid=vm_id)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  gui = Gui()
  sys.exit(gui.exec())