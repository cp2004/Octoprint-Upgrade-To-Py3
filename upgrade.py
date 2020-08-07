#    OctoPrint Upgrade To Python 3: Move an existing install over from py2 to 3
#    Copyright (C) 2020  Charlie Powell
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# PYTHON 3 Check - this script can only run on Python 3
import sys
if sys.version_info.major != 3:
    print("This script will only run on python 3")
    print("Run using 'python3 upgrade.py'")
    sys.exit(0)

import os
import json
import subprocess
import zipfile
import re
import time
import queue

# CONSTANTS
SCRIPT_VERSION = '2.0.0'
LATEST_OCTOPRINT = '1.4.2'

BASE = '\033['
PROGRESS_FRAMES = [
    '      ',
    '.     ',
    '..    ',
    '...   ',
    '....  ',
    '..... ',
    '......',
]
PROGRESS_WHEEL_Q = queue.Queue()
PATH_TO_OCTOPI_VERSION = '/etc/octopi_version'


# Base classes, used throughout the script
class TextColors:
    RESET = BASE + '39m'
    RED = BASE + '31m'
    GREEN = BASE + '32m'
    YELLOW = BASE + '33m'


class TextStyles:
    BRIGHT = BASE + '1m'
    NORMAL = BASE + '22m'


# ------------------
# Useful utilities
# ------------------
def print_c(msg, color, style=None, end='\n'):
    if not style:
        print(color, msg, TextColors.RESET, sep="", end=end)
    else:
        print(color, style, msg, TextColors.RESET, TextStyles.NORMAL, end=end, sep="")


def progress_wheel(base):
    """
    Adds an animated progress indicator. MUST BE RUN AS A THREAD as it will block.
    Put anything in PROGRESS_WHEEL_Q to stop it.

    Args:
        base (str): String to be used as the base of the indicator (Example: "Loading")
    """
    while PROGRESS_WHEEL_Q.empty():
        for frame in PROGRESS_FRAMES:
            print('\r{}{}'.format(base, frame), end='')
            if not PROGRESS_WHEEL_Q.empty():
                PROGRESS_WHEEL_Q.get()  # Get and throw away message, we need to end
                return
            time.sleep(0.15)


def run_sys_command(command, custom_parser=False, sudo=False):
    output = []
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE
    )
    last_state = None
    while True:
        output_line = process.stdout.readline().decode('utf-8')
        poll = process.poll()
        if output_line == '' and process.poll() is not None:
            break
        if output_line:
            if callable(custom_parser):
                last_state = custom_parser(output_line, last_state)
            if sudo and 'sudo' in output_line:
                print(output_line, end="")
            output.append(output_line)

    return output, poll


def get_python_version(venv_path):
    """
    For some reason, running `python --version` logs to stdout... So we will handle accordingly
    Runs system command `python --version` and returns output

    Returns:
        list: List of output lines
        int: Exit Code from the process
    """
    output = []
    process = subprocess.Popen(
        ['{}/bin/python'.format(venv_path), '--version'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    last_state = None
    while True:
        output_line_stderr = process.stderr.readline().decode('utf-8')
        poll = process.poll()
        if output_line_stderr == '' and process.poll() is not None:
            break
        if output_line_stderr:
            output.append(output_line_stderr)

    return output, poll

def bail(msg):
    print_c(msg, TextColors.RED)
    sys.exit(1)


def cleanup(path_to_zipfile):
    print("\nCleaning up...")
    os.remove(path_to_zipfile)


def confirm_to_go(msg="Press [enter] to continue or ctrl-c to quit"):
    """Waits for user to press enter(True) or ctrl-c(False), then returns bool of which"""
    print(msg)
    try:
        input()  # ctrl-c is caught here
        return True
    except KeyboardInterrupt:
        return False


# ---------------------
# Actions to take. Roughly in order of execution in the script
# ---------------------
def start_text():
    print("OctoPrint Upgrade to Py 3 (v{})\n".format(SCRIPT_VERSION))
    print("Hello!")
    print("This script will move your existing OctoPrint configuration from Python 2 to Python 3")
    print_c("This script requires an internet connection ", TextColors.YELLOW, end='')  # These will print on same line
    print_c("and it will disrupt any ongoing print jobs.", TextColors.RED, TextStyles.BRIGHT)
    print("\nIt will install the latest version of OctoPrint ({}) and all plugins.".format(LATEST_OCTOPRINT))
    print("No configuration or other files will be overwritten\n")


def get_sys_info():
    """Finds out whether the underlying OS is compatible with this script

    Returns:
        2 tuple: platform valid, octopi valid
    """
    valid = sys.platform == 'linux'
    octopi = False
    if valid:
        if os.path.isfile(PATH_TO_OCTOPI_VERSION):
            valid = validate_octopi_ver()  # 0.16 <= ver < 0.18
            if not valid:
                print_c("Your OctoPi install does not support upgrading OctoPrint to Python 3 - "
                        "Please upgrade your install.", TextColors.RED)
                print_c("Details: TODO", TextColors.RED)  # TODO Link to some kind of FAQ about what to do
            octopi = True
        else:
            octopi = False
    return valid, octopi


def validate_octopi_ver():
    """
    Supported versions of OctoPi are 0.16 an 0.17.
    0.15 and earlier do not have required dependencies installed.
    """
    # TODO Thorougly test this, I hope it works
    valid = False
    major = minor = patch = 0

    with open(PATH_TO_OCTOPI_VERSION, 'r') as version_file:
        for line in version_file:
            if line:  # Make sure the line is not empty
                try:
                    major, minor, patch = line.split(".")  # TODO use regex for this... .split is too unreliable
                except Exception as e:
                    if not major or not minor or not major:
                        print("Problem accessing OctoPi version number, falling back to manual input")
                        print(e)
                        valid = False
    if major or minor or patch:
        if int(major) == 0:
            if 16 <= int(minor) < 18:
                valid = True

    print("OctoPi version: {}.{}.{}".format(major, minor, patch.replace("\n", "")))
    return valid


def test_octoprint_version(venv_path):
    output, exit_code = run_sys_command(['{}/bin/python'.format(venv_path), '-m', 'octoprint', '--version'])
    if exit_code != 0 or not output:
        bail("Failed to find OctoPrint install\n"
             "If you are not on OctoPi, please check you entered the correct path to your virtual environment")
    version_no = re.search(r"(?<=version )(.*)", output[0]).group().split('.')
    print("OctoPrint version: {}.{}.{}".format(version_no[0], version_no[1], version_no[2]))
    if int(version_no[0]) >= 1 and int(version_no[1]) >= 4:
        return True
    else:
        # This is not strictly needed, but since I am only testing this against OctoPrint 1.4.0 or later
        # I cannot guarantee behaviour of previous versions, and users should be running something recent anyway.
        return False


def get_env_config(octopi):
    sys_commands = {}
    venv_path = None
    config_base = None
    if octopi:  # TODO Validate these paths? To check user has not messed something up
        venv_path = "/home/pi/oprint"
        sys_commands['stop'] = "sudo service octoprint stop"
        sys_commands['start'] = "sudo service octoprint start"
        config_base = "/home/pi/.octoprint"
    else:
        print("Please provide the path to your virtual environment and the config directory of OctoPrint")
        print("On OctoPi, this would be /home/pi/oprint and commands 'sudo service octoprint stop/start'")
        while not venv_path:
            path = input("Path: ")
            if os.path.isfile("{}/bin/python".format(path)):
                valid = check_venv_python(path)
                if valid:
                    venv_path = path
                    print_c("Path valid", TextColors.GREEN)
                else:
                    print_c("Virtual environment is already Python 3, are you sure you need an upgrade?\n"
                            "Please try again", TextColors.YELLOW)
            else:
                print_c("Invalid venv path, please try again", TextColors.YELLOW)
            if path.endswith('/'):
                print_c("Please enter your path without a trailing slash", TextColors.YELLOW)
                venv_path = None

        while not config_base:
            conf = input("Config directory: ")
            if os.path.isfile(os.path.join(conf, 'config.yaml')):
                print_c("Config directory valid", TextColors.GREEN)
                config_base = conf
            else:
                print_c("Invalid path, please try again", TextColors.RED)

        print("\nTo do the install, we need the service stop and start commands. "
              "(Leave blank if you don't have a service set up)")
        sys_commands['stop'] = input("Stop command: ")
        sys_commands['start'] = input("Start command: ")

    return venv_path, sys_commands, config_base


def check_venv_python(venv_path):
    version_str, poll = get_python_version(venv_path)
    for line in version_str:
        match = re.search(r"^Python (?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$", line.rstrip())
        if match:
            major, minor, patch = match.group('major'), match.group('minor'), match.group('patch')
            if int(major) == 2:
                return True
            elif int(major) == 3:
                return False
    return False


def create_backup(venv_path, config_path):
    """Create OctoPrint backup and return the path to it

    Args:
        venv_path (str): path to virtual environment
        config_path (str): path to config directory base

    Returns:
        str: path to backup zip file
    """
    print("Reading installed plugins...")

    command = ["{}/bin/python".format(venv_path), "-m", "octoprint", "plugins", "backup:backup", "--exclude",
               "timelapse", "--exclude", "uploads"]
    output, poll = run_sys_command(command)
    if poll != 0:
        print_c("ERROR: Failed to create OctoPrint backup", TextColors.RED)
        bail("Fatal error, exiting")

    backup_path_line = None
    for line in output:
        if 'Creating' in line:
            backup_path_line = line

    if not backup_path_line:
        print_c("ERROR: Could not find path to backup", TextColors.RED)
        bail("Fatal error, exiting")

    zip_name = re.search(r'(?<=Creating backup at )(.*)(?=.zip)', backup_path_line).group()
    backup_path = '{}/data/backup/{}.zip'.format(config_path, zip_name)

    return backup_path


def read_plugins_from_backup(backup_path):
    # Load plugin list from zip
    with zipfile.ZipFile(backup_path, 'r') as zip_ref:
        try:
            zip_ref.getinfo("plugin_list.json")
        except KeyError:
            # no plugin list
            plugin_list = None
        else:
            # read in list
            with zip_ref.open("plugin_list.json") as plugins:
                plugin_list = json.load(plugins)

    plugin_keys = []
    if plugin_list:
        print("\nPlugins installed")
        for plugin in plugin_list:
            print("- {}".format(plugin['name']))
            plugin_keys.append(plugin['key'])
        print("If you think there is something missing from here, please check the list of plugins in Octoprint")
    else:
        print_c("No plugins found", TextColors.YELLOW)
        print("If you think this is an error, please ask for help. Note this doesn't include bundled plugins.")
    if not confirm_to_go("Press [enter] to continue or ctrl-c to quit"):
        cleanup(backup_path)
        bail("Bye!")

    return plugin_keys


def install_python3_dev(backup_path):
    print("Root access is required to install python3-dev, please fill in the password prompt if shown")
    print("Updating package list...")
    output, poll = run_sys_command(['sudo', 'apt-get', 'update'], sudo=True)
    if poll != 0:
        print_c("ERROR: failed to update package list", TextColors.RED)
        print("Please try manually")
        cleanup(backup_path)
        bail("Fatal error: Exiting")

    print("Installing python3-dev...")
    output, poll = run_sys_command(['sudo', 'apt-get', 'install', 'python3-dev', '-y'], sudo=True)
    if poll != 0:
        print_c("ERROR: failed to install python3-dev", TextColors.RED)
        print("Please try manually")
        cleanup(backup_path)
        bail("Fatal error: Exiting")
    else:
        for line in output:
            if 'newest version' in line:
                print_c(line, TextColors.GREEN)
                return
        print_c("Successfully installed python3-dev", TextColors.GREEN)


def stop_octoprint(command, backup_path):
    output, poll = run_sys_command(command.split())
    if poll != 0:
        print_c("ERROR: failed to stop OctoPrint service", TextColors.RED)
        print("Please check you specified the correct command if you are on a manual install")
        cleanup(backup_path)
        bail("Fatal Error: Exiting")


def create_new_venv(venv_path, backup_path):
    def failed(backup_path, msg):
        print_c("ERROR: Failed to create Python 3 venv", TextColors.RED)
        print_c(msg, TextColors.RED)
        cleanup(backup_path)
        bail("Fatal Error: Exiting")

    print("Creating new Python 3 environment...")
    output, poll = run_sys_command(['mv', venv_path, '{}.bak'.format(venv_path)])
    if poll != 0:
        failed(backup_path, "Could not move existing env out of the way\n Please check you don't have anything at {}.bak".format(venv_path))
    output, poll = run_sys_command(['python', '-m', 'virtualenv', '--python=/usr/bin/python3', venv_path])
    if poll != 0:
        failed(backup_path, "Could not create new venv")

    print_c("Successfully created Python 3 environment at {}".format(venv_path), TextColors.GREEN)


def install_octoprint(venv_path, backup_path):
    print("\nInstalling OctoPrint... ", end="")
    print_c("(This may take a while - Do not cancel!)", TextColors.YELLOW)
    output, poll = run_sys_command(['{}/bin/python'.format(venv_path), '-m', 'pip', 'install', 'OctoPrint'], custom_parser=pip_output_parser)

    if poll != 0:
        print_c("ERROR: OctoPrint failed to install", TextColors.RED)
        print("To restore your previous install, download the file at: ")
        print("https://raw.githubusercontent.com/cp2004/Octoprint-Upgrade-To-Py3/master/go_back.py")
        cleanup(backup_path)
        bail("Error installing OctoPrint, cannot proceed")
    else:
        print_c("OctoPrint successfully installed!", TextColors.GREEN)


def pip_output_parser(line, last_state):
    if 'Collecting' in line and last_state != 'collecting':
        print("Collecting required packages")
        return 'collecting'
    if 'Installing' in line and last_state != 'installing':
        print("Installing collected packages")
        return 'installing'
    if 'error' in line.lower():
        print("Error installing package")
        print_c(line, TextColors.RED)
    else:
        return last_state


def install_plugins(venv_path, plugin_keys, backup_path):
    try:
        import requests
    except ImportError:
        print_c("requests not installed - installing now")
        output, poll = run_sys_command(['{}/bin/python'.format(venv_path), '-m', 'pip', 'install', 'requests'])
        if poll != 0:
            print_c("requests failed to install", TextColors.RED)
            print("This is a required dependency to install plugins. Do you want to continue without installing plugins?")
            if not confirm_to_go():
                return
        import requests

    print("\nDownloading OctoPrint's plugin repo")
    response = requests.get('https://plugins.octoprint.org/plugins.json')
    if not response.ok:
        print("Plugin repo couldn't be reached")
        print("Do you want to continue without installing plugins?")
        if not confirm_to_go():
            return

    plugin_repo = response.json()
    plugins_to_install = []
    for plugin in plugin_repo:
        if plugin['id'] in plugin_keys:
            plugins_to_install.append({'id': plugin['id'], 'url': plugin['archive'], 'name': plugin['title']})
            plugin_keys.remove(plugin['id'])
    print("")

    plugin_errors = []
    for plugin in plugins_to_install:
        print("Installing {}".format(plugin['name']))
        output, poll = run_sys_command([venv_path, '-m', 'pip', 'install', plugin['url']], custom_parser=pip_output_parser)
        if poll != 0:
            print_c("ERROR: Plugin {} failed to install".format(plugin['name']), TextColors.RED)
            plugin_errors.append(plugin)
        else:
            print_c("Plugin {} successfully installed".format(plugin['name']), TextColors.GREEN)

    if len(plugin_errors):
        print_c("Failed to install these plugins:", TextColors.YELLOW)
        for plugin in plugin_errors:
            print("- {}, url: {}".format(plugin['name'], plugin['url']))
        print_c("They were found on the plugin repo but failed to install", TextColors.YELLOW)

    if len(plugin_keys):
        print_c("These plugins were not found on the repo", TextColors.YELLOW)
        print("Please install them manually, from OctoPrint's plugin manager")
        for not_found_plugin in plugin_keys:
            print("- {}".format(not_found_plugin))


def start_octoprint(command):
    output, poll = run_sys_command(command.split())
    if poll != 0:
        print_c("Error starting OctoPrint service", TextColors.RED)
        print("You will need to start it yourself")


def end_text(venv_path):
    print_c("Finished! OctoPrint should be ready to go", TextColors.GREEN)
    print("Once you have verified the install works, you can safely remove the folder {}.bak".format(venv_path))
    print("If you want to go back (If it doesn't work) to Python 2 download the file at: ")
    print("https://raw.githubusercontent.com/cp2004/Octoprint-Upgrade-To-Py3/master/go_back.py")  # TODO Point to tagged release point, to prevent confusion.


if __name__ == '__main__':
    start_text()
    if not confirm_to_go():
        bail("Bye!")

    # Validate system info
    print("Detecting system info...")
    sys_valid, octopi_valid = get_sys_info()
    if not sys_valid:
        bail("Looks like your OS is not linux, or the OctoPi version number is un-readable")
    path_to_venv, commands, config_dir = get_env_config(octopi_valid)

    print("Getting OctoPrint version...")
    octoprint_greater_140 = test_octoprint_version(path_to_venv)
    if not octoprint_greater_140:
        bail("Please upgrade to an OctoPrint version >= 1.4.0 for Python 3 compatibility")

    # Create backup & read plugin list
    backup_location = create_backup(path_to_venv, config_dir)
    plugin_keys = read_plugins_from_backup(backup_location)

    # Install python3-dev
    # backup_location is passed to these so that they can clean up in the event of an error
    install_python3_dev(backup_location)

    # Install OctoPrint
    if commands['stop']:
        stop_octoprint(commands['stop'], backup_location)
    create_new_venv(path_to_venv, backup_location)
    install_octoprint(path_to_venv, backup_location)
    if len(plugin_keys):
        install_plugins(path_to_venv, plugin_keys, backup_location)
    if commands['start']:
        start_octoprint(commands['start'])

    cleanup(backup_location)
    end_text(path_to_venv)
