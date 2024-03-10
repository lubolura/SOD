#!/usr/bin/env python3

import sys
import os
import subprocess
import platform
import cv2
#import pip
import pkgutil
from datetime import datetime
from configparser import NoOptionError


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def debug(message, pipe="stdout"):
    _time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if pipe == "stderr":
        sys.stderr.write("{:s} {:s}\n".format(_time, message))
    else:
        sys.stdout.write("{:s} {:s}\n".format(_time, message))
    sys.stdout.flush()


def is_platform_windows():
    return platform.system() == "Windows"


def is_platform_linux():
    return platform.system() == "Linux"


def is_service_running():
    stat = subprocess.call(["systemctl", "is-active", "--quiet", "sod"])
    return stat == 0


def can_by_showed():
    if is_platform_windows():
        return True
    if is_platform_linux():
        if not is_service_running():
            return True
    return False


def get_from_config(config, section, option, required=True, default=None):
    try:
        val = config.get(section, option)
    except NoOptionError:
        if required:
            debug("{:s}:{:s} is required".format(section, option), "stderr")
            sys.exit(1)
        else:
            val = default

    return val

def get_list_of_dicts_from_config(config, section, option, required=True, default=None):
    try:
        val = config.get(section, option)
    except NoOptionError:
        if required:
            debug("{:s}:{:s} is required".format(section, option), "stderr")
            sys.exit(1)
        else:
            val = default
    try:
        val = list(eval(val))
    except:
        debug("{:s}:{:s} is required".format(section, option), "stderr")
        if required:
            sys.exit(1)
    return val

def get_float_from_config(config, section, option, required=True, default=None):

    try:
        val = config.getfloat(section, option)
    except NoOptionError:
        if required:
            debug("{:s}:{:s} is required".format(section, option), "stderr")
            sys.exit(1)
        else:
            val = default
    except ValueError:
        debug("{:s}:{:s}: unable to convert string to float".format(section,
              option), "stderr")
        sys.exit(1)

    return val




def get_int_from_config(config, section, option, required=True, default=None):
    try:
        val = config.getint(section, option)
    except NoOptionError:
        if required:
            debug("{:s}:{:s} is required".format(section, option), "stderr")
            sys.exit(1)
        else:
            val = default
    except ValueError:
        debug("{:s}:{:s}: unable to convert string to integer".format(section,
              option), "stderr")
        sys.exit(1)

    return val


def get_bool_from_config(config, section, option, required=True, default=None):

    try:
        val = config.getboolean(section, option)
    except NoOptionError:
        if required:
            debug("{:s}:{:s} is required".format(section, option), "stderr")
            sys.exit(1)
        else:
            val = default
    except ValueError:
        debug("{:s}:{:s}: unable to convert string to boolean".format(section,
              option), "stderr")
        sys.exit(1)

    return val



############ soem usefull windows routines
def win_DetectCameraIndex():
    openCvVidCapIds = []
    for i in range(10):
      try:
          cap = cv2.VideoCapture(i)
          if cap is not None and cap.isOpened():
             openCvVidCapIds.append(i)
      except:
          pass
    print(str(openCvVidCapIds))


def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def log_running():
    debug(f"Running in venv: {is_venv()}","stdout")
    debug(f'Python Executable: {sys.executable}',"stdout")
    debug(f'Python Version: {sys.version}',"stdout")
    debug(f'Virtualenv: {os.getenv("VIRTUAL_ENV")}',"stdout")
    #debug(f"Instaled packages : {[{x[0]:x[1]} if x[1][0] != '_' else '' for x in list(pkgutil.iter_modules())]}","stdout")



#wmi = win32com.client.GetObject ("winmgmts:")
#for usb in wmi.InstancesOf ("Win32_USBController"):
#    print(usb.Caption,usb.Description,usb.Name,usb.SystemName)

#for usb in wmi.InstancesOf ("Win32_PnPEntity"):
#    print(usb.Caption,usb.Description,usb.Name,usb.SystemName)

