#!/usr/bin/env python3
import sys
if sys.version_info.major != 3:
    print("This script will only run on python 3")
    print("Run using 'python3 upgrade.py'")
    sys.exit(0)

import os
import json
import subprocess
import zipfile
import requests
import re

BASE = '\033['


class TextColors:
    RESET = BASE + '39m'
    RED = BASE + '31m'
    GREEN = BASE + '32m'
    YELLOW = BASE + '33m'


class TextStyles:
    BRIGHT = BASE + '1m'
    NORMAL = BASE + '22m'


def oprint_version_gt_141(venv_path):
    try:
        output = subprocess.run(
            ['{}/bin/python'.format(venv_path), '-m', 'octoprint', '--version'],
            check=True,
            capture_output=True
        ).stdout.rstrip().decode('utf-8')
    except subprocess.CalledProcessError:
        print("{}Failed to find OctoPrint install{}".format(TextColors.RED, TextColors.RESET))
        print("If this is not OctoPi, please check that you have specified the right virtual env")
        sys.exit(0)

    version_no = re.search(r"(?<=version )(.*)", output).group().split('.')
    print("OctoPrint version: {}.{}.{}".format(version_no[0], version_no[1], version_no[2]))
    if int(version_no[0]) >= 1 and int(version_no[1]) >= 4:
        if int(version_no[2]) > 0:
            return True
        else:
            return False
    else:
        # This is not strictly needed, but since I am only testing this against OctoPrint 1.4.0 or later
        # I cannot guarantee behaviour of previous versions
        print("{}Please upgrade to an OctoPrint version >= 1.4.0 for Python 3 compatibility{}".format(TextColors.YELLOW, TextColors.RESET))
        sys.exit(0)


# Intro text

print("OctoPrint Upgrade from Python 2 to Python 3 (v1.1)")
print("{}This script requires an internet connection {}and {}{}it will disrupt any ongoing print jobs.{}{}".format(
    TextColors.YELLOW, TextColors.RESET, TextColors.RED, TextStyles.BRIGHT, TextColors.RESET, TextStyles.NORMAL))
print("It will install the latest OctoPrint (1.4.0) and all plugins.")
print("No configuration or other files will be overwritten")
confirm = input("Press {}[enter]{} to continue or ctrl-c to quit".format(TextColors.GREEN, TextColors.RESET))


# Detect OctoPi or prompt for paths
PATH_TO_VENV = None
CONFBASE = None
if os.path.isfile("/etc/octopi_version"):
    print("\n{}Detected OctoPi installation{}".format(TextColors.GREEN, TextColors.RESET))
    PATH_TO_VENV = "/home/pi/oprint"
    STOP_COMMAND = "sudo service octoprint stop"
    START_COMMAND = "sudo service octoprint start"
    print("Checking version")
    OPRINT_GT_141 = oprint_version_gt_141(PATH_TO_VENV)
    if not OPRINT_GT_141:
        CONFBASE = "/home/pi/.octoprint"
else:
    print("\n{}Detected manual installation{}".format(TextColors.GREEN, TextColors.RESET))
    print("Please provide the path to your virtual environment and the config directory of octoprint")
    while not PATH_TO_VENV:
        path = input("Path: ")
        if os.path.isfile("{}/bin/python".format(path)):
            print("Venv found")
            PATH_TO_VENV = path
        else:
            print("Invalid venv path, please try again")
    print("Checking version")
    OPRINT_GT_141 = oprint_version_gt_141(PATH_TO_VENV)
    if not OPRINT_GT_141:
        while not CONFBASE:
            CONFBASE = input("Config directory: ")
            if os.path.isfile(os.path.join(CONFBASE, 'config.yaml')):
                print("{}Config directory valid{}".format(TextColors.GREEN, TextColors.RESET))
            else:
                print("{}Invalid path, please try again{}".format(TextColors.GREEN, TextColors.RESET))
                CONFBASE = None
    print("\nTo do the install, we need the service stop and start commands.")
    STOP_COMMAND = input("Stop command: ")
    START_COMMAND = input("Start command: ")


# Create backup to read the plugin list
print("\nCreating a backup so we can read the plugin list")
try:
    backup_output = subprocess.run(
        ["{}/bin/python".format(PATH_TO_VENV), "-m", "octoprint", "plugins", "backup:backup", "--exclude", "timelapse", "--exclude", "uploads"],
        check=True,
        capture_output=True
    ).stdout.rstrip().decode('utf-8')
except subprocess.CalledProcessError:
    print("{}Error getting backup from OctoPrint{}".format(TextColors.RED, TextColors.RESET))
    sys.exit(0)

if OPRINT_GT_141:
    backup_target = re.search(r'(?<=Backup located at )(.*)(?=.zip)', backup_output).group()
else:
    octoprint_zip_name = re.search(r'(?<=Creating backup at )(.*)(?=.zip)', backup_output).group()
    backup_target = '{}/data/backup/{}'.format(CONFBASE, octoprint_zip_name)


# Extract plugin_list.json from the backup
with zipfile.ZipFile('{}.zip'.format(backup_target), 'r') as zip_ref:
    try:
        zip_ref.getinfo("plugin_list.json")
    except KeyError:
        # no plugin list
        plugin_list = None
    else:
        # read in list
        with zip_ref.open("plugin_list.json") as plugins:
            plugin_list = json.load(plugins)


# Generate a list of installed plugin keys
if plugin_list:
    print("\nPlugins installed:")
    plugin_keys = []
    for plugin in plugin_list:
        print("- {}".format(plugin['name']))
        plugin_keys.append(plugin['key'])
    print("If you think there is something missing from here, please check the list of plugins in Octoprint")
    go = input("Continue? {}[enter]{}".format(TextColors.GREEN, TextColors.RESET))
else:
    plugin_keys = []
    print("{}No plugins found{}".format(TextColors.YELLOW, TextColors.RESET))
    print("If you think this is an error, please ask for help. Note this doesn't include bundled plugins.")
    go = input("Press {}[enter]{} to continue, or ctrl-c to quit".format(TextColors.GREEN, TextColors.RESET))


# Move octoprint venv, create new one, install octoprint
PATH_TO_PYTHON = '{}/bin/python'.format(PATH_TO_VENV)  # Note this is the VIRTUALENV python
commands = [
    STOP_COMMAND.split(),
    ['mv', PATH_TO_VENV, '{}.bak'.format(PATH_TO_VENV)],
    ['virtualenv', '--python=/usr/bin/python3', PATH_TO_VENV],  # Only time we want to use system python
    [PATH_TO_PYTHON, '-m', 'pip', 'install', 'OctoPrint']
]
print("\nCreating Python 3 virtual environment and installing OctoPrint... {}(This may take a while - Do not cancel!){}".format(TextColors.YELLOW, TextColors.RESET))
for command in commands:
    try:
        output = subprocess.run(
            command,
            check=True,
            capture_output=True
        ).stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print("{}ERROR: Failed to install OctoPrint{}".format(TextColors.RED, TextColors.RESET))
        print(e)
        # Remove zip
        print("\nCleaning Up...")
        os.remove("{}.zip".format(backup_target))
        print("Exiting")
        sys.exit(0)
print("{}Octoprint successfully installed{}".format(TextColors.GREEN, TextColors.RESET))

# Create list of plugin urls, then install one by one
if len(plugin_keys):
    # Get the plugin repo
    print("\nFetching octoprint's plugin repo")
    PLUGIN_REPO = requests.get('https://plugins.octoprint.org/plugins.json').json()
    plugin_urls = []
    for plugin in PLUGIN_REPO:
        if plugin['id'] in plugin_keys:
            plugin_urls.append(plugin['archive'])
            plugin_keys.remove(plugin['id'])

    # Install plugins that were installed to the new env
    print("\nReinstalling plugins...")
    plugin_errors = []
    for plugin in plugin_urls:
        print("Installing {}".format(plugin))
        try:
            cmd_output = subprocess.run(
                [PATH_TO_PYTHON, '-m', 'pip', 'install', plugin],
                check=True,
                capture_output=True
            ).stdout.rstrip().decode('utf-8')
        except subprocess.CalledProcessError as e:
            plugin_errors.append(plugin[plugin])
            print("{}Error installing plugin{}".format(TextColors.RED, TextColors.RESET))
            print(e)
    if len(plugin_errors):
        print("{}Could not install these plugins:{}".format(TextColors.YELLOW, TextColors.RESET))
        for plugin in plugin_errors:
            print(" - {}".format(plugin))
        print("Reasons for this could be: \n- Not on the repository (Installed from uploaded archive/url) \n- Incompatible with your system")
        print("It is recommended that you reinstall them when you log back into OctoPrint")

    # Print plugins that were not on the repo
    print("\n{}These plugins were not found on the repo{}".format(TextColors.YELLOW, TextColors.RESET))
    print("Please install them manually, from OctoPrint's Plugin manager")
    for not_found_plugin in plugin_keys:
        for plugin in plugin_list:
            if plugin['key'] == not_found_plugin:
                print("- {}, ".format(plugin['name']))

# Restart OctoPrint, and clean up
print("\nStarting OctoPrint")
try:
    cmd_output = subprocess.run(
        START_COMMAND.split(),
        check=True,
        capture_output=True
    ).stdout.rstrip().decode('utf-8')
except subprocess.CalledProcessError as e:
    print("{}Error starting the OctoPrint service{}".format(TextColors.RED, TextColors.RESET))
    print("You will need to restart it yourself")
    print(e)

print("\nCleaning Up...")
os.remove("{}.zip".format(backup_target))
print("\n{}Finished! Octoprint should be restarted and ready to go{}".format(TextColors.GREEN, TextColors.RESET))
print("Once you have verified the install works, you can safely remove the folder {}.bak".format(PATH_TO_VENV))
