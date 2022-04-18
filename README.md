# Installation

## Everyone (See "Development" below)
Run the following command to install the executables for the client and GUI:

```
pip install -r requirements.txt
pip install .
```

Now you can run the following:

```
# CLI
pve-vdi-client <pve_vmid>
# GUI
pve-vdi-client-gui
```

## Raspberry Pi
To run this on Raspberry Pi, you need to actually use system python and pip to install the PySide2 package. To do this, run the following command:

```
sudo apt install python3-pyside2.qtgui
# It will error out on PySide2, but that's fine since you've installed it system-wide.
pip install -r requirements.txt
pip install .
```

Now you can run the following:

```
# CLI
pve-vdi-client <pve_vmid>
# GUI
pve-vdi-client-gui
```

If you're planning on wanting to hear things from your VMs over SPICE when on the RPi, make sure you install the following packages. Otherwise, audio will not work:

```
sudo apt install pulseaudio gstreamer1.0-pulseaudio gstreamer1.0-alsa
```

# Configuration
There are two locations in which the application will look for configurations (in order):
1. `~/.pve_vdi_client.cfg`
1. `.pve_vdi_client.cfg`

For information about what configuration parameters are allowed and what they mean, check out the `.pve_vdi_client.cfg.example` file at the root of this project. **It is important to note that changes to configuration that are made in the GUI will be applied to thie configuration when VMs are fetched.**

# Development
## Getting started

Run the following to get things set up:

```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install --editable .
```

If you want to run the cli or gui, run the following:

```
python -m pve_vdi_client <pve_vmid>
python -m pve_vdi_client.vdi_gui.gui
```

Have fun!

## Publishing
To publish packages to PyPi, you'll need to have a .pypirc file configured. If you need help with that, check out [this guide](https://packaging.python.org/en/latest/specifications/pypirc/). First off, build the distributable packages:

```
python -m build
```

Once the package is built, you should have both an archive and wheel package in the `dist/` directory. Now, run the following command to upload it to the relevant repo:

```
twine upload --config-file .pypirc --repository homelab-pip dist/pve_vdi_client-0.0.2-py3-none-any.whl
```