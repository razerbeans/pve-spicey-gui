import re

from configparser import ConfigParser
from pathlib import Path
from proxmoxer import ProxmoxAPI
from subprocess import Popen

from proxmoxer.core import ResourceException

class ClientException(Exception):
  pass

class Client(ProxmoxAPI):
  def spice_proxy(self, **vmkwargs):
    vm = self.get_vm(**vmkwargs)
    if not vm:
      raise ClientException("Node not found")
    return self.nodes(vm['node']).qemu(vm['vmid']).spiceproxy.post(proxy=vm['node'])

  def get_vm(self, include_config=False, **kwargs):
    for vm in self.cluster_vms(include_config=include_config):
      if all([k in vm and re.fullmatch(str(v), str(vm[k])) for k, v in kwargs.items()]):
        return vm
    return None

  def get_vms(self, include_config=False, **kwargs):
    result = []
    for vm in self.cluster_vms(include_config=include_config):
      if all([k in vm and re.fullmatch(str(v), str(vm[k])) for k, v in kwargs.items()]):
        result.append(vm)
    return result

  def cluster_vms(self, include_config=True):
    vms = []
    for node in self.nodes.get():
      [vms.append({**vm, **{"node": node['node']}}) for vm in self.nodes(node['node']).qemu.get()]
      if include_config is True:
        for idx, vm in enumerate(vms):
          try:
            vm_config = self.nodes(node['node']).qemu(vm['vmid']).config.get()
            vms[idx] = {**vm, **vm_config}
          except ResourceException as e:
            pass
    return vms

  def write_spice_proxy_file(self, file_out_name=Path("spiceproxy"), **vmkwargs):
    proxy_contents = self.spice_proxy(**vmkwargs)
    spice_config_ini_file = ConfigParser()
    spice_config_ini_file['virt-viewer'] = proxy_contents
    with open(file_out_name, 'w') as file:
      spice_config_ini_file.write(file)
    return file_out_name

  def spice_connect(self, remote_viewer_bin_path='remote-viewer', **vmkwargs):
    spiceproxy_file = self.write_spice_proxy_file(**vmkwargs)
    Popen([remote_viewer_bin_path, str(spiceproxy_file)])