import os
import subprocess

print("This script will move your old installation back (Just in case!)")
print("Only use it if you have used the upgrade script and it failed")
PATH_TO_VENV = None
CONFBASE = None
if os.path.isfile("/etc/octopi_version"):
    print("\nDetected OctoPi installation")
    PATH_TO_VENV = "/home/pi/oprint"
    STOP_COMMAND = "sudo service octoprint stop"
    START_COMMAND = "sudo service octoprint start"
else:
    print("\nManual install detected")
    print("Please provide the path to your virtual environment")
    while not PATH_TO_VENV:
        path = input("Path: ")
        if os.path.isfile("{}/bin/python".format(path)):
            print("Venv found")
            PATH_TO_VENV = path
        else:
            print("Invalid venv path, please try again")
    print("\nTo revert the install, we need the service stop and start commands for OctoPrint")
    STOP_COMMAND = input("Stop command: ")
    START_COMMAND = input("Start command: ")

COMMANDS = [
    STOP_COMMAND.split(),
    ['mv', PATH_TO_VENV, '{}FAIL.bak'.format(PATH_TO_VENV)],
    ['mv', '{}.bak'.format(PATH_TO_VENV), PATH_TO_VENV],
    START_COMMAND.split()
]
for command in COMMANDS:
    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True
        ).stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print("Failed to restore backup")
        print(e)

print("Successfully reverted to the old install")
print("Before reverting another failed install you should remove the folder {}FAIL.bak".format(PATH_TO_VENV))
