""" This module seaches the operating system for devices on serial ports
"""
# TODO: Find the origin of this code and give credit

import glob
import sys
from sys import platform
from typing import Callable, List

import serial

import settings
from snr.utils.utils import attempt, sleep


def get_port_to_use(dbg: Callable, set_port: Callable) -> str:
    """ Finds a serial port for the serial connection

    Calls the serial_finder library to search the operating system
    for serial ports
    """
    port = None

    def try_find_port() -> bool:
        try:
            # Get a list of all serial ports
            dbg('serial_finder', "Searching for serial ports")
            ports = list_ports()
            dbg('serial_finder', "Found ports:")
            for p in ports:
                dbg('serial_finder', p)
            # Select the port
            port = select_port(dbg,ports)
            set_port(port)
            if(port is None):
                raise Exception("Serial Exception")
            dbg("serial_finder", "Using port: {}", [port])
            return True

        except Exception as error:
            dbg("serial_finder", "Error finding port: {}", [str(error)])
            return False

    def failure(tries: int):
        dbg('serial_finder',
                 "Could not find serial port after {} attempts. Crashing now.",
                 [tries])
        exit("Could not find port")

    def fail_once():
        dbg('serial_finder', "Failed to find serial port, trying again.")
        sleep(settings.SERIAL_RETRY_WAIT)  # Wait a second before retrying

    attempt(try_find_port,
            settings.SERIAL_MAX_ATTEMPTS,
            fail_once,
            failure)

    return port


def list_ports() -> list:
    """ Finds all serial ports and returns a list containing them

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)    # Try to open a port
            s.close()                  # Close the port if sucessful
            result.append(port)        # Add to list of good ports
        except (OSError, Exception):   # If un sucessful
            pass
    return result


def select_port(dbg: Callable, ports: List[str]) -> str or None:
    """ Selects the apprpriate port from the given list
    """
    if platform == "linux" or platform == "linux2":
        dbg("serial_finder", "Linux detected")
        for p in ports:
            # return '/dev/ttyS0'
            # # If using raspi GPIO for serial, just pick this port
            if ("USB" in p) or ("ACM" in p):
                return p

    elif platform == "darwin":
        dbg("serial_finder", "Darwin detected")
        return ports[0]

    elif platform == "win32":
        dbg("serial_finder", "Windows detected")
        p = ""
        for p in ports:
            dbg("serial_finder", p)
        return p

    else:
        return None
