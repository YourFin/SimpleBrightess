#!/bin/python3
import sys
import math

def moveBrightness(argument):
    """
    :type argument: str
    :return:
    """
    import glob
    import configparser
    import os

    def check_bool_config(config, option, section="Config"):
        """

        :type config: configparser.ConfigParser
        :type option: str
        :type section: str
        :return: bool
        """
        try:
            return config.getboolean(section, option)
        except configparser.Error:
            return False



    def check_option_folder_exists(config, option, section = "Config"):
        """

        :type config: configparser.ConfigParser
        :type section: str
        :type option: str
        :return: bool
        """
        try:
            return config.has_option(section, option) & os.path.isdir(config.get(section, option))
        except (NotADirectoryError, FileExistsError, FileNotFoundError, configparser.Error):
            return False


    def check_option_file_exists(config, option, section = "Config"):
        """

        :type config: configparser.ConfigParser
        :type section: str
        :type option: str
        :return: bool
        """
        try:
            return config.has_option(section, option) & os.path.isfile(config.get(section, option))
        except (FileNotFoundError, IsADirectoryError, configparser.Error):
            return False

    config = configparser.ConfigParser()

    # Try to find a config file
    try:
        config.read_file(open(os.path.expanduser("~/.backlightKeys")))
    except FileNotFoundError:
        pass
    try:
        config.read_file(open(os.path.expanduser("~/.config/backlightKeys")))
    except FileNotFoundError:
        pass

    # Find path to backlight dir (e.g. /sys/class/backlight/intel_backlight)
    if check_option_folder_exists(config, "backlightPath"):
        backlightPath = config.get("Config", 'backlightPath')
    else:
        sysBacklights = glob.glob('/sys/class/backlight/*')
        if sysBacklights.__len__() == 0:
            pass
        elif sysBacklights.__len__() == 1:
            backlightPath = sysBacklights[0]
        else:
            pass

    # Check if brightness file is defined, else default
    if check_option_file_exists(config, "brightnessFilePath"):
        brightnessFilePath = config.get("Config", "brightnessFilePath")
    else:
        brightnessFilePath = backlightPath + '/brightness'

    # Check if max_brightness file is defined, else default
    if check_option_file_exists(config, "max_brightness"):
        max_brightnessFilePath = config.get("Config", "max_brightnessFilePath")
    else:
        max_brightnessFilePath = backlightPath + '/max_brightness'

    # Grab number of presses from full to no brightness Default 10
    try:
        numPresses = config.getint("Config", "numPresses")
    except (FileNotFoundError, configparser.NoSectionError, configparser.NoOptionError):
        numPresses = 10

    # Check if a gamma scale is in use
    try:
        gamma = config.getfloat("Config", "Gamma")
    except (FileNotFoundError, configparser.NoSectionError, configparser.NoOptionError):
        gamma = 2

    # Grab percent jump per press, if manually set. If not, calculate it
    try:
        numPerPress = config.getfloat("Config", "valPerJump")
    except (FileNotFoundError, configparser.NoSectionError, configparser.NoOptionError):
        try:
            with open(max_brightnessFilePath) as ff:
                maxBrightness = int(float(ff.readline()))
        except FileNotFoundError:
            maxBrightness = 100
        finally:
            numPerPress = math.pow(maxBrightness, 1.0/gamma) / numPresses






    # Calculate and apply new brighness value
    with open(brightnessFilePath, '+r') as brightnessFile:
        brightness = int(float(brightnessFile.readline()))
        if argument.lower() == "up":
            brightness = math.pow(math.pow(brightness, 1.0/gamma) + numPerPress, gamma)
            if brightness > maxBrightness:
                brightness = maxBrightness
        elif argument.lower() == "down":
            if brightness == 1 & check_bool_config(config, "allowOff"):
                brightness = 0
            elif brightness > 1:
                try:
                    brightness = math.pow(math.pow(brightness, 1.0/gamma) - numPerPress, gamma)
                except ValueError:
                    brightness = 1
        brightnessFile.truncate()
        bleh = str(int(brightness))
        brightnessFile.write(bleh)
    return brightness

moveBrightness(sys.argv[1])

