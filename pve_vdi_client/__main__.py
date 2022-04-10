from optparse import OptionParser
from decouple import config
from pve_vdi_client.vdi_client.client import Client

if __name__ == '__main__':
  usage = "usage: pve_vdi_client [options] pve_vmid"
  parser = OptionParser(usage=usage)
  parser.add_option("-u", "--user", dest="user", default=config('USERNAME', default=None),
                    help="User to use for connecting to Proxmox's API")
  parser.add_option("-p", "--password", dest="password", default=config('PASSWORD', default=None),
                    help="Password for selected user")
  parser.add_option('-s', "--server", dest="host", default=config('SERVER', default=None),
                    help="Server URL to connect to")
  parser.add_option('-k', '--verify-ssl', dest="verify_ssl",
                    action="store_false",
                    default=config('VERIFY_SSL', default=True, cast=bool),
                    help="Verify server SSL certificate")
  (options, args) = parser.parse_args()
  proxmox_client = Client(**vars(options))
  proxmox_client.spice_connect(vmid=int(args[0]))
