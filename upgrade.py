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
import time
import queue
import threading

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
    """Checks the OctoPrint version. Will exit if OctoPrint is not 1.4.0 or higher

    Args:
        venv_path (str): Path to the venv of OctoPrint

    Returns:
        bool: True if OctoPrint >= 1.4.1, else False
    """
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


progress_frames = [
    '      ',
    '.     ',
    '..    ',
    '...   ',
    '....  ',
    '..... ',
    '......',
]
LOADING_PRINTING_Q = queue.Queue()


def progress_wheel(base):
    while LOADING_PRINTING_Q.empty():
        for frame in progress_frames:
            print('\r{}{}'.format(base, frame), end='')
            if not LOADING_PRINTING_Q.empty():
                LOADING_PRINTING_Q.get()
                return
            time.sleep(0.15)


# Intro text
print("OctoPrint Upgrade from Python 2 to Python 3 (v1.3.2)")
print("{}This script requires an internet connection {}and {}{}it will disrupt any ongoing print jobs.{}{}".format(
    TextColors.YELLOW, TextColors.RESET, TextColors.RED, TextStyles.BRIGHT, TextColors.RESET, TextStyles.NORMAL))
print("It will install the latest OctoPrint (1.4.0) and all plugins.")
print("No configuration or other files will be overwritten")
try:
    confirm = input("Press {}[enter]{} to continue or ctrl-c to quit".format(TextColors.GREEN, TextColors.RESET))
except KeyboardInterrupt:
    print("\nBye!")
    sys.exit(0)


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
    print("Please provide the path to your virtual environment and the config directory of OctoPrint")
    while not PATH_TO_VENV:
        path = input("Path: ")
        if os.path.isfile("{}/bin/python".format(path)):
            print("{}Venv found{}".format(TextColors.GREEN, TextColors.RESET))
            PATH_TO_VENV = path
        else:
            print("{}Invalid venv path, please try again{}".format(TextColors.RED, TextColors.RESET))
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
    try:
        go = input("Continue? {}[enter]{}".format(TextColors.GREEN, TextColors.RESET))
    except KeyboardInterrupt:
        print("\nCleaning Up...")
        os.remove("{}.zip".format(backup_target))
        print("Bye!")
        sys.exit(0)
else:
    plugin_keys = []
    print("{}No plugins found{}".format(TextColors.YELLOW, TextColors.RESET))
    print("If you think this is an error, please ask for help. Note this doesn't include bundled plugins.")
    try:
        go = input("Press {}[enter]{} to continue, or ctrl-c to quit".format(TextColors.GREEN, TextColors.RESET))
    except KeyboardInterrupt:
        print("\nCleaning Up...")
        os.remove("{}.zip".format(backup_target))
        print("Bye!")
        sys.exit(0)

# Install python3-dev as it is not installed by default on OctoPi
print("\nRoot access is required to install python3-dev, please fill in the password prompt if shown")
print("Updating package list")
process = subprocess.Popen(
    ['sudo', 'apt-get', 'update'],
    stdout=subprocess.PIPE
)
while True:
    output = process.stdout.readline().decode('utf-8')
    poll = process.poll()
    if output == '' and poll is not None:
        print("\r\033[2K", end="")
        break
    if output:
        if 'sudo' in output:
            print(output, end="")
if process.poll() != 0:
    print("{}ERROR: failed to update package list{}".format(TextColors.RED, TextColors.RESET))
    print("Please try manually")
    print("Exiting")

print("Installing python3-dev")
process = subprocess.Popen(
    ['sudo', 'apt-get', 'install', 'python3-dev', '-y'],
    stdout=subprocess.PIPE
)
while True:
    output = process.stdout.readline().decode('utf-8')
    poll = process.poll()
    if output == '' and poll is not None:
        print("\r\033[2K", end="")
        break
    if output:
        if 'sudo' in output:
            print(output, end="")
if process.poll() != 0:
    print("{}ERROR: python3-dev failed to install{}".format(TextColors.RED, TextColors.RESET))
    print("Please try manually")
    print("Exiting")
else:
    print("{}Successfully installed python3-dev{}".format(TextColors.GREEN, TextColors.RESET))

print("")
# Move OctoPrint venv, create new one, install OctoPrint
PATH_TO_PYTHON = '{}/bin/python'.format(PATH_TO_VENV)  # Note this is the VIRTUALENV python
loading_thread = threading.Thread(target=progress_wheel, args=("Creating Python 3 virtual environment",))
loading_thread.start()
commands = [
    STOP_COMMAND.split(),
    ['mv', PATH_TO_VENV, '{}.bak'.format(PATH_TO_VENV)],
    ['virtualenv', '--python=/usr/bin/python3', PATH_TO_VENV],  # Only time we want to use system python
]
for command in commands:
    try:
        output = subprocess.run(
            command,
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        LOADING_PRINTING_Q.put("KILL")
        loading_thread.join()
        print("{}ERROR: Failed to create Python 3 venv{}".format(TextColors.RED, TextColors.RESET))
        print("Please check you do not have a folder at {}.bak".format(PATH_TO_VENV))
        # Remove zip
        print("\nCleaning Up...")
        os.remove("{}.zip".format(backup_target))
        print("Exiting")
        sys.exit(0)
LOADING_PRINTING_Q.put('KILL')
loading_thread.join()
print("\r\033[2K{}Python 3 virtual environment created{}".format(TextColors.GREEN, TextColors.RESET))

print("\nInstalling OctoPrint {}(This may take a while - Do not cancel!){}".format(TextColors.YELLOW, TextColors.RESET))
process = subprocess.Popen(
    [PATH_TO_PYTHON, '-m', 'pip', 'install', 'OctoPrint'],
    stdout=subprocess.PIPE
)
loading_thread = threading.Thread(target=progress_wheel, args=("(Installing OctoPrint)",))
loading_thread.start()
last_output = None
while True:
    output = process.stdout.readline().decode('utf-8')
    poll = process.poll()
    if output == '' and poll is not None:
        LOADING_PRINTING_Q.put('KILL')
        loading_thread.join()
        print("\r\033[2K", end="")
        break
    if output:
        if 'Collecting' in output:
            if 'octoprint' in output:
                if last_output != 'octoprint':
                    print("\r\033[2KDownloading OctoPrint")
                    last_output = 'octoprint'
            else:
                if last_output != 'dependencies':
                    print("\r\033[2KDownloading dependencies")
                    last_output = 'dependencies'
        elif 'Installing' in output:
            if last_output != 'install':
                print("\r\033[2KInstalling OctoPrint and its dependencies")
                last_output = 'install'

if process.poll() != 0:
    print("{}ERROR: OctoPrint failed to install{}".format(TextColors.RED, TextColors.RESET))
    print("To restore your previous install, download the file at: ")
    print("https://raw.githubusercontent.com/cp2004/Octoprint-Upgrade-To-Py3/master/go_back.py")
    print("Exiting")
    sys.exit(0)
else:
    print("{}Octoprint successfully installed{}".format(TextColors.GREEN, TextColors.RESET))


# Create list of plugin urls, then install one by one
if len(plugin_keys):
    print("\nFetching OctoPrint's plugin repo")
    PLUGIN_REPO = requests.get('https://plugins.octoprint.org/plugins.json').json()
    plugins_to_install = []
    # Dictionary structure should be as follows:
    # {key:{url:xxx, name:xxx}, key2:{url:xxx, name:xxx}}
    for plugin in PLUGIN_REPO:
        if plugin['id'] in plugin_keys:
            plugins_to_install.append({'id': plugin['id'], 'url': plugin['archive'], 'name': plugin['title']})
            plugin_keys.remove(plugin['id'])
    print("")
    # Install plugins that were previously installed (to the new env)
    loading_thread = threading.Thread(target=progress_wheel, args=("Reinstalling plugins",))
    loading_thread.start()
    plugin_errors = []
    for plugin in plugins_to_install:
        process = subprocess.Popen(
            [PATH_TO_PYTHON, '-m', 'pip', 'install', plugin['url']],
            stdout=subprocess.PIPE
        )
        last_output = None
        while True:
            output = process.stdout.readline().decode('utf-8')
            poll = process.poll()
            if output == '' and poll is not None:
                print("\r\033[2K", end="")
                break
            if output:
                if 'Collecting' in output:
                    if last_output != 'download':
                        print("\r\033[2KDownloading {}".format(plugin['name']))
                        last_output = 'download'
                elif 'Installing' in output:
                    if last_output != 'install':
                        print("\r\033[2KInstalling {}".format(plugin['name']))
                        last_output = 'install'

        if process.poll() != 0:
            print("{}ERROR: Plugin {} failed to install{}".format(TextColors.RED, plugin['name'], TextColors.RESET))
            plugin_errors.append(plugin['name'])
        else:
            print("{}{} successfully installed{}".format(TextColors.GREEN, plugin['name'], TextColors.RESET))

    LOADING_PRINTING_Q.put("KILL")
    loading_thread.join()
    print("\r\033[2K")

    if len(plugin_errors):
        print("{}Could not install these plugins:".format(TextColors.YELLOW))
        for plugin in plugin_errors:
            print("- {}".format(plugin))
        print("They were found on the repository but failed to install{}".format(TextColors.RESET))

    # Print plugins that were not on the repo
    if len(plugin_keys):
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
print("If you want to go back (If it doesn't work) to Python 2 download the file at: ")
print("https://raw.githubusercontent.com/cp2004/Octoprint-Upgrade-To-Py3/master/go_back.py")
