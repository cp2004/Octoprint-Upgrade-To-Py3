#!/usr/bin/env python3
import sys
if sys.version_info.major != 3:
    print("This script will only run on python 3")
    print("Run using 'python3 go_back.py'")
    sys.exit(0)

import os
import subprocess

BASE = '\033['


class TextColors:
    RESET = BASE + '39m'
    RED = BASE + '31m'
    GREEN = BASE + '32m'
    YELLOW = BASE + '33m'


class TextStyles:
    BRIGHT = BASE + '1m'
    NORMAL = BASE + '22m'


print("OctoPrint upgrade to Python 3: go_back.py (v1.1)")
print("This script will move your old installation back (Just in case!)")
print("{}Only use it if you have used the upgrade script and it failed{}".format(TextColors.YELLOW, TextColors.RESET))
print("Warning: There have been reports of this script failing, if it fails for you please report it to me as soon as possible. Thanks!")
try:
    go = input("Press {}[enter]{} to continue, or ctrl-c to stop".format(TextColors.GREEN, TextColors.RESET))
except KeyboardInterrupt:
    print("\nBye!")
    sys.exit(0)


PATH_TO_VENV = None
CONFBASE = None
if os.path.isfile("/etc/octopi_version"):
    print("\n{}Detected OctoPi installation{}".format(TextColors.GREEN, TextColors.RESET))
    PATH_TO_VENV = "/home/pi/oprint"
    STOP_COMMAND = "sudo service octoprint stop"
    START_COMMAND = "sudo service octoprint start"
else:
    print("\n{}Manual install detected{}".format(TextColors.GREEN, TextColors.RESET))
    print("Please provide the path to your virtual environment")
    while not PATH_TO_VENV:
        path = input("Path: ")
        if os.path.isfile("{}/bin/python".format(path)):
            print("{}Venv found{}".format(TextColors.GREEN, TextColors.RESET))
            PATH_TO_VENV = path
        else:
            print("{}Invalid venv path, please try again{}".format(TextColors.RED, TextColors.RESET))
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
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE
    )
    while True:
        output = process.stdout.readline().decode('utf-8')
        poll = process.poll()
        if output == '' and poll is not None:
            break
    if process.poll() != 0:
        print("{}ERROR: failed to restore backup{}".format(TextColors.RED, TextColors.RESET))
        print("Please try manually")
        print("Exiting")
        sys.exit(0)

print("Successfully reverted to the old install")
print("Before reverting another failed install you should remove the folder {}FAIL.bak".format(PATH_TO_VENV))
