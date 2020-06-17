#!/usr/bin/env python3

import os
import json
import subprocess
import zipfile
import requests


print("This script is about to perform an upgrade of your OctoPrint install from python 2 to 3")
print("WORK IN PROGRESS - Does not actually do anything to your install! (Yet)")
confirm = input("Press [enter] to continue or ctrl-c to quit")

PATH_TO_VENV = None
if os.path.isfile("/etc/octopi_version"):
    print("Detected OctoPi installation")
    PATH_TO_VENV = "/home/pi/oprint"
    STOP_COMMAND = "sudo service octoprint stop"
    START_COMMAND = "sudo service octoprint start"
    CONFBASE = "/home/pi/.octoprint/"
else:
    print("OctoPi install not detected")
    print("Please provide the path to your virtual environment and the config directory of octoprint")
    while not PATH_TO_VENV:
        path = input("Path: ")
        if os.path.isfile("{}/bin/python".format(path)):
            print("Venv found")
            PATH_TO_VENV = path
        else:
            print("Invalid venv path, please try again")
    CONFBASE = input("Config directory: ")
    print("To do the install, we need the service stop and start commands.")
    STOP_COMMAND = input("Stop command: ")
    START_COMMAND = input("Start command: ")

print("\nCreating a backup so we can read the plugin list")
octoprint_zip_name = subprocess.check_output(
    "{}/bin/octoprint plugins backup:backup --exclude timelapse --exclude uploads | grep -oP '(?<=Creating backup at )(.*)(?=.zip)'".format(PATH_TO_VENV)
).rstrip()

backup_target = '{}/data/backup/{}'.format(CONFBASE, octoprint_zip_name)

print("Extracting plugin_list.json from backup")
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

if len(plugin_list):
    print("\nPlugins installed:")
    plugin_keys = []
    for plugin in plugin_list:
        print("- {}".format(plugin['name']) + item['name'])
        plugin_keys.append(plugin['key'])
    print("If you think there is something missing from here, please check the list of plugins in Octoprint")
    go = input("Continue? [enter]")
else:
    print("No plugins found")
    print("If you think this is an error, please ask for help. Note this doesn't include bundled plugins.")
    go = input("Press [enter] to continue, or ctrl-c to quit")


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

if len(plugin_keys):
    # Get the plugin repo
    print("Fetching octoprint's plugin repo")
    PLUGIN_REPO = requests.get('https://plugins.octoprint.org/plugins.json').json()
    plugin_urls = []
    for plugin in PLUGIN_REPO:
        if plugin['id'] in plugin_keys:
            plugin_urls.append(plugin['archive'])

    # Install plugins that were installed to the new env
    print("\nReinstalling plugins...")
    for plugin in plugin_urls:
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
