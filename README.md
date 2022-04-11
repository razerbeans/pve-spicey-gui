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