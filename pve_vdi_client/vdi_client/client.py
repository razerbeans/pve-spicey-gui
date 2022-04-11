from configparser import ConfigParser
from pathlib import Path
from proxmoxer import ProxmoxAPI
from subprocess import Popen

class Client(ProxmoxAPI):
  def spice_proxy(self, **vmkwargs):
    vm = self.get_vm(**vmkwargs)
    return self.nodes(vm['node']).qemu(vm['vmid']).spiceproxy.post(proxy=vm['node'])

  def get_vm(self, **kwargs):
    for vm in self.cluster_vms():
      if all([vm[k] == v for k, v in kwargs.items()]):
        return vm
    return None

  def cluster_vms(self):
    vms = []
    for node in self.nodes.get():
      [vms.append({**vm, **{"node": node['node']}}) for vm in self.nodes(node['node']).qemu.get()]
    return vms

  def write_spice_proxy_file(self, file_out_name=Path("spiceproxy"), **vmkwargs):
    proxy_contents = self.spice_proxy(**vmkwargs)
    spice_config_ini_file = ConfigParser()
    spice_config_ini_file['virt-viewer'] = proxy_contents
    with open(file_out_name, 'w') as file:
      spice_config_ini_file.write(file)
    return file_out_name

  def spice_connect(self, **vmkwargs):
    spiceproxy_file = self.write_spice_proxy_file(**vmkwargs)
    Popen(['remote-viewer', str(spiceproxy_file)])