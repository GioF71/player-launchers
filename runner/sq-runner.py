#!/usr/bin/env python3

import os
import time
from pathlib import Path
from enum import Enum
import exceptions


class VariableName(Enum):
    SQUEEZELITE_BINARY = "SQUEEZELITE_BINARY"
    SQUEEZELITE_RESTART_ON_FAIL = "SQUEEZELITE_RESTART_ON_FAIL"
    SQUEEZELITE_RESTART_DELAY = "SQUEEZELITE_RESTART_DELAY"
    SQUEEZELITE_SERVER_PORT = "SQUEEZELITE_SERVER_PORT"
    SQUEEZELITE_AUDIO_DEVICE = "SQUEEZELITE_AUDIO_DEVICE"
    SQUEEZELITE_TIMEOUT = "SQUEEZELITE_TIMEOUT"
    SQUEEZELITE_LINEAR_VOLUME = "SQUEEZELITE_LINEAR_VOLUME"
    SQUEEZELITE_NAME = "SQUEEZELITE_NAME"
    SQUEEZELITE_MODEL = "SQUEEZELITE_MODEL"


class CommandLineOptionMapperData:

    def __init__(
            self,
            var_name: str,
            cmd_line_option: str,
            dflt_value: str = None,
            boolean_value: bool = False,
            in_quotes: bool = False):
        self.__var_name: str = var_name
        self.__cmd_line_option: str = cmd_line_option
        self.__dflt_value: str = dflt_value
        self.__boolean_value: bool = boolean_value
        self.__in_quotes: bool = in_quotes

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
    def in_quotes(self) -> bool:
        return self.__in_quotes


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
    SQUEEZELITE_TIMEOUT = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_TIMEOUT.value,
        cmd_line_option="-C",
        dflt_value=3)
    SQUEEZELITE_LINEAR_VOLUME = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_LINEAR_VOLUME.value,
        cmd_line_option="-X",
        boolean_value=True)
    SQUEEZELITE_NAME = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_NAME.value,
        cmd_line_option="-n",
        in_quotes=True)
    SQUEEZELITE_MODEL = CommandLineOptionMapperData(
        var_name=VariableName.SQUEEZELITE_MODEL.value,
        cmd_line_option="-m",
        in_quotes=True)

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
    def in_quotes(self) -> bool:
        return self.value.in_quotes


class LauncherOption(Enum):
    SQUEEZELITE_BINARY = LauncherOptionData(
        var_name=VariableName.SQUEEZELITE_BINARY.value,
        dflt_value="/usr/bin/squeezelite")
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
    default: str = "no"
    if default and isinstance(default, bool):
        dflt_value_str = "yes" if default else "no"
    elif default and isinstance(default, str):
        dflt_value_str = yes_no_or_empty(default)
    v: str = yes_no_or_empty(getenv(key, dflt_value_str))
    return v == "yes"


def getenv(key: str, default: str = None) -> str:
    return os.getenv(key, default)


def add_command_line_option(
        command_line: str,
        mapper: CommandLineOptionMapper) -> str:
    v: str = getenv(mapper.var_name, mapper.dflt_value)
    if mapper.boolean_value and v and v.lower() == "yes":
        # add selected flag
        command_line = f"{command_line} {mapper.cmd_line_option}"
    elif not mapper.boolean_value and v:
        print(f"Using [{v}] for parameter [{mapper.cmd_line_option}] ...")
        mapped_value: str = v if not mapper.in_quotes else f"\"{v}\""
        command_line = f"{command_line} {mapper.cmd_line_option} {mapped_value}"
    return command_line


def main():
    fallback_sq_binary: str = "squeezelite"
    sq_default_binary: Path = Path(LauncherOption.SQUEEZELITE_BINARY.value.dflt_value)
    if sq_default_binary.is_file():
        # file exists
        fallback_sq_binary = str(sq_default_binary.resolve(strict=True))
    sq_binary: str = getenv(LauncherOption.SQUEEZELITE_BINARY.value.var_name, fallback_sq_binary)
    print(f"squeezelite runner is using [{sq_binary}]")
    command_line: str = sq_binary
    mapper: CommandLineOptionMapper
    for mapper in CommandLineOptionMapper:
        command_line = add_command_line_option(
            command_line=command_line,
            mapper=mapper)
    restart_on_fail: bool = getenv_as_bool(
        key=LauncherOption.SQUEEZELITE_RESTART_ON_FAIL.var_name,
        default=LauncherOption.SQUEEZELITE_RESTART_ON_FAIL.dflt_value)
    restart_delay: int = int(must_be_int(getenv(
        key=LauncherOption.SQUEEZELITE_RESTART_DELAY.var_name,
        default=LauncherOption.SQUEEZELITE_RESTART_DELAY.dflt_value)))
    print(f"Restart on fail: [{restart_on_fail}] delay: [{restart_delay}]")
    while True:
        print(f"Executing [{command_line}] ...")
        res: int = os.system(command_line)
        print(f"Result: [{res}] type [{type(res)}]")
        if res == 0 or not restart_on_fail:
            break
        else:
            # wait the configured amount of time
            time.sleep(restart_delay)


if __name__ == "__main__":
    main()
