# TUTello

TUTello is the TUPilots' hub for Tello programming with a Python interface. There is a lot to be done, from creating a user interface, to creating autonomous systems with computer vision.

## Table of Contents
1. [Setup](#setup)
2. [Virtual Environment](#virtualenvironment)
3. [Git](#git)
4. [Documentation](#documentation)

## Setup

Clone this repository with `git clone https://github.com/TUPilotsClub/TUTello.git`

## Virtual Environment

Using a virtual environment greatly reduces issues with installing packages. It starts you with a fresh install, and you can download just the packages you need. I recommend `venv`.

### venv setup

1. Install `venv` with `pip install virtualenv`

2. Navigate to the root directory, `TUTello`

3. Enter the command `python -m venv venv` (or try `python3`)

4. `./venv/Scripts/activate` (you might need to use `activate.bat` or `activate.ps1`)

   - On Mac, do `. venv/bin/activate`

5. `pip install -r requirements.txt`

### using venv

1. Activate using `./venv/Scripts/activate` (you might need to use `activate.bat` or `activate.ps1`)

2. Deactivate using `deactivate`

## Git

Git is a system to manage code between different people and versions. You will primarily do work on a different branch so that code does not conflict.

Here is a reference guide for different commands: https://confluence.atlassian.com/bitbucketserver/basic-git-commands-776639767.html

Here are the highlights:

1. To create/use a branch: `git checkout -b <branch_name>` (drop the `-b` after the first time)

2. To add files to the save list: `git add <file_name>`

3. To save locally: `git commit -m '<description_of_changes>'`

4. To publish saved changes to GitHub: `git push origin <branch_name>`

5. To retrieve others' changes: `git pull`

## Documentation

There are a number of different components to the codebase

1. `drone`
   - contains `tello.py` which houses the Tello class to control the drone.
   - import: `from drone.tello import Tello`.
   - instantiate: `tello = Tello()`.
   - `tello.connect()` initializes the drone.
   - `tello.takeoff()` and `tello.land()` cause the drone to takeoff and land.
   - `tello.send_rc_control(<roll_speed>,<pitch_speed>,<thrust_speed>,<yaw_speed>)` controls the movement.

2. `gui`
   - contains classes for creating a pygame window with the Tello video feed.
   - `GUI` accepts a list of components to display and handles key events.
   - `SimpleGUI` accepts a `VideoFeed` and creates a `VideoComponent` to be displayed in the `GUI`.
   
2. `video`
   - `VideoFeed` is a base class for handling video streams.
      - child classes can perform some filter on the Tello video in `get_frame()`.
   - `RedballVideo` is a `VideoFeed` which uses image processing to identify red objects.
   - `FacetrackVideo`is a `VideoFeed` which uses a library to track faces.

3. `controller`
   - contains classes for controlling the movement of the Tello.
   - `Controller` is a base class for sending rc commands to the Tello.
   - `SimpleController` gets keyboard input from pygame and controls movement.
   - `Telemetry` is an interface to get telemetry data from the Tello.
      - Child classes can be used to get telemetry from other sources (like video)
   
4. `scripts`
   - various scripts that utilize the above modules
   - `guiprogram.py` creates a SimpleGUI window with a SimpleController