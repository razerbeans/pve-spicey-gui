import pytest
from proxmoxer.backends.https import AuthenticationError

from pve_vdi_client.vdi_client.client import Client

@pytest.mark.vcr()
def test_client_instantiation_with_valid_credentials():
  proxmox_client = Client(host='pve.example.com', 
                          user='thinclient@pve',
                          password='hate')
  assert proxmox_client

@pytest.mark.vcr()
def test_client_instantiation_with_invalid_credentials():
  with pytest.raises(AuthenticationError):
    Client(host='pve.example.com', 
           user='thinclient@pve',
           password='hate')
