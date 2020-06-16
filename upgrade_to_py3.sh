#! /bin/bash
echo "This script is about to perform an upgrade of your OctoPrint install from python 2 to 3"

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
$PATH_TO_OCTOPRINT plugins backup:backup --exclude timelapse --exclude uploads