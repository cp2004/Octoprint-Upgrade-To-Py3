# Upgrade your OctoPrint install to Python 3!

Many new plugins only support Python 3, and do not support Python 2 anymore. If you get a message like this installing a plugin:

```
ERROR: Package 'OctoDash-Companion' requires a different Python: 2.7.16 not in '>=3.3, <4'
```

You need to upgrade your OctoPrint install to use Python 3, rather than Python 2.

You have several options, depending on how you have installed OctoPrint:

* **OctoPi users**: [Re-flash your OS](#re-flashing-your-os) to upgrade to OctoPi 0.18 which uses Python 3 for OctoPrint
* **OctoPi users**: [Use this script](#using-this-script) to upgrade your OctoPi 0.17 install to use Python 3
* **Linux users**: [Use this script](#using-this-script) to upgrade if your system has at least Python 3.6 installed.
* **Windows/MacOS users**: You will need to re-do your virtual environment installation. See ['What can I do if my system is not supported'](#what-do-i-do-if-my-system-is-not-supported) below.


## Re-flashing your OS

This is the easiest way to upgrade if you are using OctoPi, since you can re-flash the base OS and it is using Python 3.

1. Take a backup from inside OctoPrint's 'Backup and Restore' tab, and download it.
2. Download & install [OctoPi 0.18](https://octoprint.org/download)
3. Once installed, you can restore your backup using 'Backup and Restore' again.


## Using this script

### Requirements

* Python 3.6+ installed as `python3` on the system
* Linux install
* OctoPrint 1.4.0+ for Python 3 compatibility.
  **Note**: The script will install the latest stable version of OctoPrint when you run it.

If you don't meet the above requirements, then please see ['What can I do if my system is not supported'](#what-do-i-do-if-my-system-is-not-supported) below.

### Running the script

Run the following 2 commands in the terminal to start the upgrade:

```
curl -L https://get.octoprint.org/py3/upgrade.py --output upgrade.py
python3 upgrade.py
```

If you are not running OctoPi, you will be prompted to provide:
  - The path to the venv (`/home/pi/oprint` on OctoPi)
  - Configuration directory (`/home/pi/.octoprint`)
  - Command to stop (`sudo service octoprint stop`)
  - Command to start (`sudo service octoprint start`)

You may also be asked to provide the `sudo` password so the script can install `python3-dev`, a package required to install some plugins. (If your machine is not running passwordless sudo)

**Once the install has finished** (and you have tested it works, of course) you can safely remove the folder `/path/to/venv.bak` containing your old Python 2 environment. 

On an OctoPi install, this would be at `/home/pi/oprint.bak`

## Command line options
There are two command line options available, which you can use. Both optional:
* `-f` or `--force`: Forces through any 'confirmations' where you would have to press enter to continue. Note that you may still need to enter your configuration or sudo password.
* `-c` or `--custom`: Force use of custom input, as would be standard on non-OctoPi installs. Useful if you have multiple installs, but started on OctoPi.

## Returning to the old install

If the install fails, then you can safely return to the old install by restoring the backup. It is just the old environment renamed, so you can move it back to it's original position.

You can use the other script in this repo, [go_back.py](https://github.com/cp2004/Octoprint-Upgrade-To-Py3/blob/master/go_back.py) to return to the old install. Usage is similar to the upgrade script:

```
curl -L https://raw.githubusercontent.com/cp2004/Octoprint-Upgrade-To-Py3/master/go_back.py --output go_back.py
python3 go_back.py
```

## What do I do if my system is not supported?

### OctoPi 0.16 or earlier

OctoPrint is only compatible with Python 3.6+. As a result, on earlier versions of OctoPi that were not based on Debian Buster, it is not possible to run this script on those OctoPi versions, since they don't have a new enough Python install available.

#### Recommended route to Python 3

* Follow the [Re-flash your OS instructions](#re-flashing-your-os) above

### Manual installs

If you are running Windows, MacOS or your system does not work with this script for whatever reason, then you will need to perform the upgrade manually.

The basic steps boil down to this:

* Create a backup of your OctoPrint install (not available on Windows)
* Save a copy of your current virtual environment
* Create a new virtual environment based on Python 3
* Install OctoPrint in the virtual environment
* Restore the backup you downloaded earlier.

For more detailed steps, please refer to the OS specific install guides [on the download page](https://octoprint.org/download)


## Blog post
**For a full explanation of why this script is here, please make sure to read the blog post** I wrote about this on the OctoPrint blog: [Upgrade Your OctoPrint Install to Python 3!](https://octoprint.org/blog/2020/09/10/upgrade-to-py3/)

## Limitations of this script
* The script is unable to restore plugins that are not on the official repository. If it cannot find the plugin listed it will tell you and you should install them manually afterwards.

* The script is not able to tell you if your plugins are not Python 3 compatible, you will have to check in the OctoPrint plugin manager afterwards to find incompatible ones. Recommended to check *before* upgrading.

## Contributing
Please open an issue if you find something wrong, or have a feature request.
If you would like to make a PR, please do so against the `devel` branch as `master` is the download branch for users and I don't want changes that accidentally break something!
If your are making a PR for a big feature, please open an issue first so we can discuss.

## Supporting the project!
Found this script useful?

You can support my development (**cp2004**) of this script through [Github Sponsors](https://github.com/sponsors/cp2004) from as little as $1!

You can also support Gina over on the main OctoPrint project [here](https://octoprint.org/support-octoprint/)

<a href="https://www.jetbrains.com/?from=cp2004"><img align="left" width="100" height="100" src="jetbrains-variant-2.png" alt="JetBrains Logo"></a> Thanks to JetBrains for supporting an open source license for their brilliant IDEs that I use to develop my projects!
