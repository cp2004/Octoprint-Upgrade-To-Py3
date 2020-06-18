# Octoprint Upgrade To Python 3
 NOTE: This is not a plugin! A script to move an existing octoprint install from python 2 to python 3
 Only runs on linux

---
# Usage
A one time script to upgrade your OctoPrint installation from Python 2 to Python 3

It is recommended that you use the plugin [Python 3 check](https://plugins.octoprint.org/plugins/Python3PluginCompatibilityCheck/) to check your plugins are compatible before installing as any that are not Python 3 compatible will not work!
Following commands will get you to Python 3:
```
curl https://raw.githubusercontent.com/cp2004/Octoprint-Upgrade-To-Py3/master/upgrade.py --output upgrade.py
python3 upgrade.py
```
If you are not running OctoPi, you will be prompted to provide:
- The path to the venv (`/home/pi/oprint` on OctoPi)
- Configuration directory (`/home/pi/.octoprint`)
- Command to stop (`sudo service octoprint stop`)
- Command to start (`sudo service octoprint start`)

# Limitations
The script is unable to restore plugins that are not on the repository. If it cannot find the plugin listed it will list them to you and you should install them manually afterwards.

Will not tell you if the plugins are not Python 3 compatible, you will have to check in the OctoPrint plugin manager afterwards to find incompatible ones.
