# Octoprint Upgrade To Python 3
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/110c98d760aa4e088fdf5a69adcbc4a9)](https://www.codacy.com/manual/cp2004/Octoprint-Upgrade-To-Py3?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cp2004/Octoprint-Upgrade-To-Py3&amp;utm_campaign=Badge_Grade)
![Test migration](https://github.com/cp2004/Octoprint-Upgrade-To-Py3/workflows/Test%20migration/badge.svg)

A script to move an existing OctoPrint install from Python 2 to Python 3.
Only compatible with OctoPi 0.17 and up since it (and OctoPrint Py3) requires Python 3.6+

---
## Usage
A one time script to upgrade your OctoPrint installation from Python 2 to Python 3

It is recommended that you use this with the plugin [Python 3 check](https://plugins.octoprint.org/plugins/Python3PluginCompatibilityCheck/) by [jneilliii](https://github.com/jneilliii) or from OctoPrint 1.4.1 this info is in the Plugin Manager to check that your plugins are compatible before using this script as any that are not Python 3 compatible will not work!
Following commands will get you to Python 3:
```
curl https://get.octoprint.org/py3/upgrade.py --output upgrade.py
python3 upgrade.py
```
**Warning: Only compatible with OctoPi 0.17 and OctoPi 0.18 (currently dev nightly) (& Debian Buster) Previous versions do not have sufficient Python 3 versions to run OctoPrint. [See more below](https://github.com/cp2004/Octoprint-Upgrade-To-Py3#what-do-i-do-if-my-system-is-not-supported)**

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
The script saves your old environment at `path/to/env.bak` and you can use the other script in this repo, [go_back.py](https://github.com/cp2004/Octoprint-Upgrade-To-Py3/blob/master/go_back.py) to return to the old install. Particularly useful if the install fails or some plugins are not Python 3 compatible, and you want to go back to Python 2.
```
curl https://raw.githubusercontent.com/cp2004/Octoprint-Upgrade-To-Py3/master/go_back.py --output go_back.py
python3 upgrade.py
```

## What do I do if my system is not supported?
### OctoPi
OctoPrint is only compatible with python3 and above for Python 3.6+. As a result, on earlier versions of OctoPi that were not based on Debian Buster, it is not possible to run this script on those OctoPi versions. 
#### Recommended route to Python 3
Currently the recommended way to get your install running on Python 3, is to download the latest version of OctoPi (0.17) from [octoprint.org](https://get.octoprint.org). You would need to:
* Backup your current install of OctoPrint using the built-in backup function
* Flash OctoPi 0.17+ to your Raspberry Pi's SD card
* Restore the backup into the new install

You can also download OctoPi 0.18 development builds, as these come with Python 3 environments pre-installed. **Only do this if you are comfortable with development builds!**

**Note: OctoPi 0.17 comes with OctoPrint 1.3.12 - you will need to update to the same version (or greater) that your old install was before you can restore the backup**

**You also need OctoPrint 1.4.0 or later for Python 3 compatibility**

### Manual installs
You can follow similar steps to the above for OctoPi, but you would have to re-install OctoPrint manually - which you may as well do on Python 3. As a result, this script is mostly usless to you if your system is old enough to not have Py 3.6+ installed!

## Limitations
* The script is unable to restore plugins that are not on the repository. If it cannot find the plugin listed it will list them to you and you should install them manually afterwards.

* Will not tell you if the plugins are not Python 3 compatible, you will have to check in the OctoPrint plugin manager afterwards to find incompatible ones.

## Contributing
Please open an issue if you find something wrong, or have a feature request.
If you would like to make a PR, please do so against the `devel` branch as `master` is downloaded by users and I don't want changes that accidentally break something!
If your are making a PR for a feature, please open an issue first as there may be other plans in the pipeline that would be disruptive to development

## Supporting the project!
Found this script useful?

You can support my development (**cp2004**) of this script through [Github Sponsors](https://github.com/sponsors/cp2004) from as little as $1!

You can also support Gina over on the main OctoPrint project [here](https://octoprint.org/support-octoprint/)

<a href="https://www.jetbrains.com/?from=cp2004"><img align="left" width="100" height="100" src="jetbrains-variant-2.png" alt="JetBrains Logo"></a> Thanks to JetBrains for supporting an open source license for their brilliant IDEs that I use to develop my projects!
