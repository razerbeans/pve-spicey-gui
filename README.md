# Installation

## Everyone (See "Development" below)

## Raspberry Pi
To run this on Raspberry Pi, you need to actually use system python and pip to install the PySide2 package. To do this, run the following command:

```
sudo apt install python3-pyside2.qtgui
pip install -r requirements.txt
```

It will error out on PySide2, but that's fine since you've installed it system-wide. Now you can run the following:

```
# CLI
python -m pve_vdi_client <pve_vmid>
# GUI
python -m pve_vdi_client.vdi_gui.gui
```

# Development
## Getting started

Run the following to get things set up:

```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install --editable .
```

If you want to run the command line tool, run the following:

```
python -m pve_vdi_client <pve_vmid>
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