#!/usr/bin/env python3

import os
import time
from enum import Enum
import exceptions
import subprocess
import shutil


class VariableName(Enum):
    SQUEEZELITE_BINARY_PATH = "SQUEEZELITE_BINARY_PATH"
    SQUEEZELITE_RESTART_ALWAYS = "SQUEEZELITE_RESTART_ALWAYS"
    SQUEEZELITE_RESTART_ON_FAIL = "SQUEEZELITE_RESTART_ON_FAIL"
    SQUEEZELITE_RESTART_DELAY = "SQUEEZELITE_RESTART_DELAY"
    SQUEEZELITE_SERVER_PORT = "SQUEEZELITE_SERVER_PORT"
    SQUEEZELITE_AUDIO_DEVICE = "SQUEEZELITE_AUDIO_DEVICE"
    SQUEEZELITE_MIXER_DEVICE = "SQUEEZELITE_MIXER_DEVICE"
    SQUEEZELITE_TIMEOUT = "SQUEEZELITE_TIMEOUT"
    SQUEEZELITE_LINEAR_VOLUME = "SQUEEZELITE_LINEAR_VOLUME"
    SQUEEZELITE_NAME = "SQUEEZELITE_NAME"
    SQUEEZELITE_MODEL_NAME = "SQUEEZELITE_MODEL_NAME"
    SQUEEZELITE_PARAMS = "SQUEEZELITE_PARAMS"
    SQUEEZELITE_BUFFER_SIZE = "SQUEEZELITE_BUFFER_SIZE"
    SQUEEZELITE_VOLUME_CONTROL = "SQUEEZELITE_VOLUME_CONTROL"
    SQUEEZELITE_UNMUTE = "SQUEEZELITE_UNMUTE"
    SQUEEZELITE_VISUALIZER = "SQUEEZELITE_VISUALIZER"
    SQUEEZELITE_MAC_ADDRESS = "SQUEEZELITE_MAC_ADDRESS"
    SQUEEZELITE_REPORT_MAX_SAMPLE_RATE = "SQUEEZELITE_REPORT_MAX_SAMPLE_RATE"
    SQUEEZELITE_CODECS = "SQUEEZELITE_CODECS"
    SQUEEZELITE_EXCLUDE_CODECS = "SQUEEZELITE_EXCLUDE_CODECS"
    SQUEEZELITE_UPSAMPLING = "SQUEEZELITE_UPSAMPLING"
    SQUEEZELITE_RATES = "SQUEEZELITE_RATES"
    SQUEEZELITE_DELAY = "SQUEEZELITE_DELAY"
    SQUEEZELITE_PRIORITY = "SQUEEZELITE_PRIORITY"
    SQUEEZELITE_READ_FORMATS_FROM_HEADER = "SQUEEZELITE_READ_FORMATS_FROM_HEADER"
    SQUEEZELITE_POWER_SCRIPT = "SQUEEZELITE_POWER_SCRIPT"
    SQUEEZELITE_RPI_GPIO = "SQUEEZELITE_RPI_GPIO"


class CommandLineOptionMapperData:

    def __init__(
            self,
            var_name: str,
            cmd_line_option: str,
            dflt_value: str = None,
            boolean_value: bool = False,
            replace_spaces_with_colon: bool = False):
        self.__var_name: str = var_name
        self.__cmd_line_option: str = cmd_line_option
        self.__dflt_value: str = dflt_value
        self.__boolean_value: bool = boolean_value
        self.__replace_spaces_with_colon: bool = replace_spaces_with_colon

    @property
    def var_name(self) -> str:
        return self.__var_name

    @property
    def dflt_value(self) -> str:
        return self.__dflt_value

    @property
    def cmd_line_option(self) -> str:
        return self.__cmd_line_option

    @property
    def boolean_value(self) -> bool:
        return self.__boolean_value

    @property
    def replace_spaces_with_colon(self) -> bool:
        return self.__replace_spaces_with_colon


class LauncherOptionData:

    def __init__(
            self,
            var_name: str,
            dflt_value: str = None):
        self.__var_name: str = var_name
        self.__dflt_value: str = dflt_value

    @property
    def var_name(self) -> str:
        return self.__var_name

    @property
    def dflt_value(self) -> str:
        return self.__dflt_value


class CommandLineOptionMapper(Enum):
    SQUEEZELITE_SERVER_PORT = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_SERVER_PORT.value,
        cmd_line_option="-s")
    SQUEEZELITE_AUDIO_DEVICE = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_AUDIO_DEVICE.value,
        cmd_line_option="-o")
    SQUEEZELITE_MIXER_DEVICE = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_MIXER_DEVICE.value,
        cmd_line_option="-O")
    SQUEEZELITE_TIMEOUT = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_TIMEOUT.value,
        cmd_line_option="-C",
        dflt_value="5")
    SQUEEZELITE_LINEAR_VOLUME = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_LINEAR_VOLUME.value,
        cmd_line_option="-X",
        boolean_value=True)
    SQUEEZELITE_NAME = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_NAME.value,
        cmd_line_option="-n")
    SQUEEZELITE_MODEL_NAME = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_MODEL_NAME.value,
        cmd_line_option="-M")
    SQUEEZELITE_PARAMS = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_PARAMS.value,
        cmd_line_option="-a",
        replace_spaces_with_colon=True)
    SQUEEZELITE_BUFFER_SIZE = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_BUFFER_SIZE.value,
        cmd_line_option="-b",
        replace_spaces_with_colon=True)
    SQUEEZELITE_VOLUME_CONTROL = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_VOLUME_CONTROL.value,
        cmd_line_option="-V")
    SQUEEZELITE_UNMUTE = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_UNMUTE.value,
        cmd_line_option="-U")
    SQUEEZELITE_VISUALIZER = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_VISUALIZER.value,
        cmd_line_option="-v")
    SQUEEZELITE_MAC_ADDRESS = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_MAC_ADDRESS.value,
        cmd_line_option="-m",
        replace_spaces_with_colon=True)
    SQUEEZELITE_REPORT_MAX_SAMPLE_RATE = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_REPORT_MAX_SAMPLE_RATE.value,
        cmd_line_option="-Z")
    SQUEEZELITE_CODECS = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_CODECS.value,
        cmd_line_option="-c")
    SQUEEZELITE_EXCLUDE_CODECS = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_EXCLUDE_CODECS.value,
        cmd_line_option="-e")
    SQUEEZELITE_UPSAMPLING = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_UPSAMPLING.value,
        cmd_line_option="-u",
        replace_spaces_with_colon=True,
        dflt_value="E")
    SQUEEZELITE_RATES = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_RATES.value,
        cmd_line_option="-r")
    SQUEEZELITE_DELAY = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_DELAY.value,
        cmd_line_option="-D",
        dflt_value="500")
    SQUEEZELITE_PRIORITY = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_PRIORITY.value,
        cmd_line_option="-p",
        dflt_value=45)
    SQUEEZELITE_READ_FORMATS_FROM_HEADER = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_READ_FORMATS_FROM_HEADER.value,
        cmd_line_option="-W")
    SQUEEZELITE_POWER_SCRIPT = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_POWER_SCRIPT.value,
        cmd_line_option="-S")
    SQUEEZELITE_RPI_GPIO = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_RPI_GPIO.value,
        cmd_line_option="-G")

    @property
    def var_name(self) -> str:
        return self.value.var_name

    @property
    def dflt_value(self) -> str:
        return self.value.dflt_value

    @property
    def cmd_line_option(self) -> str:
        return self.value.cmd_line_option

    @property
    def boolean_value(self) -> str:
        return self.value.boolean_value

    @property
    def replace_spaces_with_colon(self) -> bool:
        return self.value.replace_spaces_with_colon


class LauncherOption(Enum):
    SQUEEZELITE_BINARY_PATH = LauncherOptionData(
        var_name=VariableName.SQUEEZELITE_BINARY_PATH.value,
        dflt_value="squeezelite")
    SQUEEZELITE_RESTART_ALWAYS = LauncherOptionData(
        var_name=VariableName.SQUEEZELITE_RESTART_ALWAYS.value,
        dflt_value="no")
    SQUEEZELITE_RESTART_ON_FAIL = LauncherOptionData(
        var_name=VariableName.SQUEEZELITE_RESTART_ON_FAIL.value,
        dflt_value="yes")
    SQUEEZELITE_RESTART_DELAY = LauncherOptionData(
        var_name=VariableName.SQUEEZELITE_RESTART_DELAY.value,
        dflt_value="3")

    @property
    def var_name(self) -> str:
        return self.value.var_name

    @property
    def dflt_value(self) -> str:
        return self.value.dflt_value


def yes_no_or_empty(v: str) -> str:
    if not v or (v.lower() in ['yes', 'no']):
        return v.lower() if v else v
    raise exceptions.NotYesNoOrEmpty(f"Value [{v}] must be empty or one between 'yes' and 'no'")


def must_be_int(v: str) -> str:
    try:
        int_v: int = int(v)
        return str(int_v)
    except ValueError:
        raise exceptions.NotAnIntegerValue(f"Value [{v}] is not an integer")


def getenv_as_bool(key: str, default: any = None) -> str:
    if default and isinstance(default, bool):
        dflt_value_str = "yes" if default else "no"
    elif default and isinstance(default, str):
        dflt_value_str = yes_no_or_empty(default)
    v: str = yes_no_or_empty(getenv(key, dflt_value_str))
    return v == "yes"


def getenv(key: str, default: str = None) -> str:
    return os.getenv(key, default)


def add_command_line_option(command_line: list[str], mapper: CommandLineOptionMapper) -> list[str]:
    v: str = getenv(mapper.var_name, mapper.dflt_value)
    if mapper.boolean_value and v and v.lower() == "yes":
        # add selected flag
        command_line += [ mapper.cmd_line_option ]
    elif not mapper.boolean_value and v:
        print(f"Using [{v}] for parameter [{mapper.cmd_line_option}] ...")
        mapped_value: str = v
        if mapper.replace_spaces_with_colon:
            mapped_value = mapped_value.replace(" ", ":")
        command_line += [ mapper.cmd_line_option, mapped_value ]
    return command_line


def main():
    # fallback_sq_binary: str = shutil.which(LauncherOption.SQUEEZELITE_BINARY_PATH.value.dflt_value)
    sq_binary: str = getenv(
        key=LauncherOption.SQUEEZELITE_BINARY_PATH.value.var_name,
        default=LauncherOption.SQUEEZELITE_BINARY_PATH.value.dflt_value)
    print(f"squeezelite runner binary [{sq_binary}]")
    sq_binary = os.path.expanduser(sq_binary)
    which_binary: str = shutil.which(sq_binary)
    command_line: list[str] = [os.path.expanduser(which_binary)]
    print(f"squeezelite runner binary -> [{command_line[0]}]")
    mapper: CommandLineOptionMapper
    for mapper in CommandLineOptionMapper:
        command_line = add_command_line_option(command_line=command_line, mapper=mapper)
    restart_anyway: bool = getenv_as_bool(
        key=LauncherOption.SQUEEZELITE_RESTART_ALWAYS.var_name,
        default=LauncherOption.SQUEEZELITE_RESTART_ALWAYS.dflt_value)
    restart_on_fail: bool = getenv_as_bool(
        key=LauncherOption.SQUEEZELITE_RESTART_ON_FAIL.var_name,
        default=LauncherOption.SQUEEZELITE_RESTART_ON_FAIL.dflt_value)
    restart_delay: int = int(must_be_int(getenv(
        key=LauncherOption.SQUEEZELITE_RESTART_DELAY.var_name,
        default=LauncherOption.SQUEEZELITE_RESTART_DELAY.dflt_value)))
    print(f"Restart on fail: [{restart_on_fail}] delay: [{restart_delay}]")
    while True:
        print(f"Executing [{command_line}] ...")
        res: int = subprocess.run(command_line, shell=False)
        print(f"Result: [{res}] type [{type(res)}] "
              f"restart_on_fail [{restart_on_fail}] "
              f"restart_delay [{restart_delay}]")
        if (restart_anyway) or (res != 0 and restart_on_fail):
            # wait the configured amount of time
            print(f"Waiting [{restart_delay}] seconds ...") 
            time.sleep(restart_delay)
            print("Retrying ...")
        else:
            print(f"Start returned [{res}], will not retry.")
            break


if __name__ == "__main__":
    main()
