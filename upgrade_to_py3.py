#!/usr/bin/env python2

import os
import json
import subprocess
import zipfile
import getpass


print("This script is about to perform an upgrade of your OctoPrint install from python 2 to 3")
print("WORK IN PROGRESS - Does not actually do anything to your install! (Yet)")
confirm = raw_input("Press [enter] to continue or ctrl-c to quit")

PATH_TO_VENV = None
if os.path.isfile("/etc/octopi_version"):
    print("Detected OctoPi installation")
    PATH_TO_VENV = "/home/pi/oprint"
    STOP_COMMAND = "sudo service octoprint stop"
    START_COMMAND = "sudo service octoprint start"
else:
    print("OctoPi install not detected")
    print("Please provide the path to your virtual environment")
    while not PATH_TO_VENV:
        path = raw_input("Path: ")
        if os.path.isfile("{}/bin/python".format(path)):
            print("Venv found")
            PATH_TO_VENV = path
        else:
            print("Invalid venv path, please try again")
    print("To do the install, we need the service stop and start commands.")
    STOP_COMMAND = raw_input("Stop command: ")
    START_COMMAND = raw_input("Start command: ")

print("\nCreating a backup so we can read the plugin list")
octoprint_zip_name = subprocess.check_output(
    "{}/bin/octoprint plugins backup:backup --exclude timelapse --exclude uploads | grep -oP '(?<=Creating backup at )(.*)(?=.zip)'".format(PATH_TO_VENV)
).rstrip()

backup_target = '/home/{}/.octoprint/data/backup/{}'.format(getpass.getuser(), octoprint_zip_name)
print("Unzipping...")
with zipfile.ZipFile('{}.zip'.format(backup_target), 'r') as zip_ref:
    zip_ref.extractall(backup_target)


if os.path.isfile(os.path.join(backup_target, 'plugin_list.json')):
    plugins_installed = True
    print("Plugins found")
else:
    plugins_installed = False
    print("No plugins found")
    print("If you think this is an error, please ask for help. Note this doesn't include bundled plugins.")
    go = raw_input("Press [enter] to continue, or ctrl-c to quit")

if plugins_installed:
    with open(os.path.join(backup_target, 'plugin_list.json'), 'r') as plugins:
        plugin_list = json.load(plugins)
        print("\nPlugins installed:")
        plugin_names = []
        for item in plugin_list:
            print("- " + item['name'])
        print("If you think there is something missing from here, please check the list of plugins in Octoprint")
        go = raw_input("Continue? [enter]")

# Move octoprint venv, create new one etc. etc.
# I'm going to leave this commented out until everything else works
PATH_TO_PYTHON = '{}/bin/python'.format(PATH_TO_VENV)  # Note this is the VIRTUALENV python
commands = [
    STOP_COMMAND,
    'mv {} {}.bak'.format(PATH_TO_VENV, PATH_TO_VENV),
    'virtualenv --python=/usr/bin/python3 {}'.format(PATH_TO_VENV),  # Only time we want to use system python
    '{} -m pip install "OctoPrint>=1.4.0"'.format(PATH_TO_PYTHON)
]
print("\nMoving venv and installing octoprint...")
for command in commands:
    print("Pretending to do: {}".format(command))
    # output = subprocess.check_output(command)


# Install plugins that were installed to the new env
print("\nReinstalling plugins...")
with open(os.path.join(backup_target, 'plugin_list.json'), 'r') as plugin_file:
    plugin_list = json.load(plugin_file)
    for plugin in plugin_list:
        print("Pretending to install {}".format(plugin['name']))
        print("{} -m pip install {}".format(PATH_TO_PYTHON, plugin['url']))
        # output = subprocess.check_output(
        #     "{} -m pip install {}".format(PATH_TO_PYTHON, plugin['url'])
        # )

print("\nStarting Octoprint")
print("Pretending to run {}".format(START_COMMAND))
# output = subprocess.check_output(START_COMMAND)

print("\nCleaning Up... \nRemoving backup zip")
os.remove("{}.zip".format(backup_target))
print("Removing backup folder")
import shutil
shutil.rmtree(backup_target)
print("Finished! Octoprint should be restarted and ready to go")
