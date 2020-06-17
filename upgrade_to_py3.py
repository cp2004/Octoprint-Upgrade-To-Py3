import os
import json
import subprocess
import zipfile
import getpass


print("This script is about to perform an upgrade of your OctoPrint install from python 2 to 3")
print("WORK IN PROGRESS")
confirm = raw_input("Press [enter] to continue or ctrl-c to quit")

PATH_TO_VENV = None
if os.path.isfile("/etc/octopi_version"):
    print("Detected OctoPi installation")
    PATH_TO_VENV = "/home/pi/oprint"
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

print("Creating a backup so we can read the plugin list")
octoprint_zip_name = subprocess.check_output(
    "{}/bin/octoprint plugins backup:backup --exclude timelapse --exclude uploads | grep -oP '(?<=Creating backup at )(.*)(?=.zip)'".format(PATH_TO_VENV),
    shell=True
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

with open(os.path.join(backup_target, 'plugin_list.json'), 'r') as plugins:
    plugin_list = json.load(plugins)
    plugin_names = []
    plugin_urls = []
    for item in plugin_list:
        plugin_names.append(item['name'])
        plugin_urls.append(item['url'])

    print("Plugins installed:")
    for name in plugin_names:
        print('- ' + name)

print(plugin_urls)

print("\nCleaning Up \nDeleting zip...")
os.remove("{}.zip".format(backup_target)
print("removing backup folder")
import shutil
shutil.rmtree(backup_target)
print("Finished! Octoprint should be restarted and ready to go")