import os

from configparser import ConfigParser
from optparse import OptionParser
from pve_vdi_client.vdi_client.client import Client


CLIENT_PATHS=['.pve_vdi_client.cfg', os.path.expanduser('~/.pve_vdi_client.cfg')]


def run():
  usage = "usage: pve_vdi_client [options] pve_vmid"
  parser = OptionParser(usage=usage)
  config = ConfigParser()
  config.read(CLIENT_PATHS)
  parser.add_option("-u", "--user", dest="user", default=config['client'].get('username', None),
                    help="User to use for connecting to Proxmox's API")
  parser.add_option("-p", "--password", dest="password", default=config['client'].get('password', None, raw=True),
                    help="Password for selected user")
  parser.add_option('-s', "--server", dest="host", default=config['client'].get('server', None),
                    help="Server URL to connect to")
  parser.add_option('-k', '--verify-ssl', dest="verify_ssl",
                    action="store_false",
                    default=config['client'].getboolean('verify_ssl', False),
                    help="Verify server SSL certificate")
  parser.add_option('-f', '--path', dest="remote_viewer_path", 
                    default=config['client'].get('remote_viewer_path', 'remote-viewer'),
                    help="Full path to remote-viewer executable")
  (options, args) = parser.parse_args()
  options_dict = dict(**vars(options))
  remote_viewer_bin_path = options_dict.pop('remote_viewer_path')
  proxmox_client = Client(**options_dict)
  proxmox_client.spice_connect(remote_viewer_bin_path=remote_viewer_bin_path, vmid=int(args[0]))


if __name__ == '__main__':
  run()