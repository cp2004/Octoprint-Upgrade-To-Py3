#! /bin/bash
echo "This script is about to perform an upgrade of your OctoPrint install from python 2 to 3"
echo "It will install jq to help manage the json files"
echo "WORK IN PROGRESS"
echo "Press [enter] to continue or ctrl-c to quit"
read

#Test if we are running OctoPi, else need path to env
OCTOPI_VERSION_FILE=/etc/octopi_version

if test -f "$OCTOPI_VERSION_FILE"; then
    echo "Detected OctoPi installation"
    PATH_TO_VENV='/home/pi/oprint'
else
    echo "OctoPi install not detected"
    echo "Please provide the path to your virtual environment"
    is_venv=false
    while [ $is_venv == false ]; do
        echo "Path: "
        read PATH_TO_VENV
        if test -f "$PATH_TO_VENV"/bin/python; then
            echo "Venv found"
            is_venv=true
        else
            echo "Invalid venv path, please try again!"
        fi
    done
fi

PATH_TO_OCTOPRINT=$PATH_TO_VENV/bin/octoprint

#Try to create a backup
echo "Creating a backup so we can read the plugin list"

BACKUP_NAME=$($PATH_TO_VENV/bin/octoprint plugins backup:backup --exclude timelapse --exclude uploads | grep -oP '(?<=Creating backup at )(.*)(?=.zip)')
PATH_TO_BACKUP=/home/$(whoami)/.octoprint/data/backup/$BACKUP_NAME.zip
echo "Backup created at " $PATH_TO_BACKUP

#Now we need to find a list of plugin urls from the backup/plugin-list.json
#And match them to the repo

BACKUP_TARGET=/home/$(whoami)/.octoprint/data/backup/$BACKUP_NAME
output=$(unzip $PATH_TO_BACKUP -d $BACKUP_TARGET)
rm $PATH_TO_BACKUP
echo "Removing zip now we've extracted it"
if test -f "$BACKUP_TARGET/plugin_list.json"; then
    PLUGINS_INSTALLED=true
    echo "Detected plugins installed"
else
    PLUGINS_INSTALLED=false
    echo "No plugins found, if this is not correct please ask for help"
    echo "(Note this does not include bundled plugins)"
fi

echo "Installing jq to manage plugin-list.json... (If not already)"
sudo apt-get install jq -y

echo "Removing backup"
rm -rf $BACKUP_TARGET