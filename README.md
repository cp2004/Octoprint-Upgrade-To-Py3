# Octoprint Upgrade To Python 3
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/110c98d760aa4e088fdf5a69adcbc4a9)](https://www.codacy.com/manual/cp2004/Octoprint-Upgrade-To-Py3?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cp2004/Octoprint-Upgrade-To-Py3&amp;utm_campaign=Badge_Grade)
![Test migration](https://github.com/cp2004/Octoprint-Upgrade-To-Py3/workflows/Test%20migration/badge.svg)

 NOTE: This is not a plugin! A script to move an existing octoprint install from Python 2 to Python 3
 
---
## Usage
A one time script to upgrade your OctoPrint installation from Python 2 to Python 3

It is recommended that you use this with the plugin [Python 3 check](https://plugins.octoprint.org/plugins/Python3PluginCompatibilityCheck/) by [jneilliii](https://github.com/jneilliii) or from OctoPrint 1.4.1 this info is in the Plugin Manager to check that your plugins are compatible before using this script as any that are not Python 3 compatible will not work!
Following commands will get you to Python 3:
```
curl https://get.octoprint.org/py3/upgrade.py --output upgrade.py
python3 upgrade.py
```
If you are not running OctoPi, you will be prompted to provide:
  - The path to the venv (`/home/pi/oprint` on OctoPi)
  - Configuration directory (`/home/pi/.octoprint`)
  - Command to stop (`sudo service octoprint stop`)
  - Command to start (`sudo service octoprint start`)

You may also be asked to provide the `sudo` password so the script can install `python3-dev`, a package required to install some plugins. (If your machine is not running passwordless sudo)

## Command line options
There are two command line options available, which you can use. Both optional :-
1. `-f` or `--force`: Forces through any 'confirmations' where you would have to press enter to continue. Note that you may still need to enter your config or sudo password.
2. `-c` or `--custom`: Force use of custom input, as would be standard on non-OctoPi installs. Useful if you have multiple installs, but started on OctoPi.

## Returning to the old install
The script saves your old environment at path/to/env.bak and you can use the other script in this repo, [go_back.py](https://github.com/cp2004/Octoprint-Upgrade-To-Py3/blob/master/go_back.py) to return to the old install. Particularly useful if the install fails or some plugins are not Python 3 compatible
```
curl https://raw.githubusercontent.com/cp2004/Octoprint-Upgrade-To-Py3/master/go_back.py --output go_back.py
python3 upgrade.py
```

## Common problems
  - Installing [Bed Level Visualiser](https://github.com/jneilliii/OctoPrint-BedLevelVisualizer) may fail if numpy fails to install. See [here](https://github.com/jneilliii/OctoPrint-BedLevelVisualizer/issues/224#issuecomment-614968499) for a fix.

## Limitations
The script is unable to restore plugins that are not on the repository. If it cannot find the plugin listed it will list them to you and you should install them manually afterwards.

Will not tell you if the plugins are not Python 3 compatible, you will have to check in the OctoPrint plugin manager afterwards to find incompatible ones.

## Contributing
Please open an issue if you find something wrong, or have a feature request.
If you would like to make a PR, please do so against the `devel` branch as `master` is downloaded by users and I don't want changes that accidentally break something!
If your are making a PR for a feature, please open an issue first as there may be other plans in the pipeline that would be disruptive to development
