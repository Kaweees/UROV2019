""" Main Python code that runs on the Raspberry Pi on robot and surface unit

This is the python program is meant to run on the Raspberry Pi's located on
the robot and one the surface unit. This program acts as a intermediary
between the Raspberry Pi on the surface unit and the Arduino/Teensy on the
robot. The scheduling module used in this program manages the serial and
sockets connections to the Arduino/Teensy and topside raspberry Pi
respectively.
"""

from sys import argv

from robot import Robot
from snr_utils import debug, print_usage, u_exit
from topside import Topside


def main():
    argc = len(argv)
    if argc < 2:
        print_usage()
        u_exit("Improper usage")

    role = str(argv[1])  # Command line argument

    mode = "deployed"

    if "-d" in argv:
        mode = "debug"

    node = None
    if role.__eq__("robot"):
        debug("framework", "Running as robot in mode: {}", [mode])
        node = Robot(mode)
    elif role.__eq__("topside"):
        debug("framework", "Running as server in mode: {}", [mode])
        node = Topside(mode)
    else:
        debug("framework", "Invalid role {} given as command line arg", [role])
        print_usage()
        u_exit("Unknown role")

    # Run the node's loop
    try:
        node.loop()
    except KeyboardInterrupt:
        print()
        debug("framework", "Interrupted by user, exiting")

    node.terminate()
    debug("framework", "Node terminated")
    u_exit("Ya done now")


if __name__ == "__main__":
    main()
