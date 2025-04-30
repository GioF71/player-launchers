#!/usr/bin/env python3

import os
from pathlib import Path
from enum import Enum


class VariableName(Enum):
    SQUEEZELITE_BINARY = "SQUEEZELITE_BINARY"
    SQUEEZELITE_SERVER_PORT = "SQUEEZELITE_SERVER_PORT"
    SQUEEZELITE_AUDIO_DEVICE = "SQUEEZELITE_AUDIO_DEVICE"


class CommandLineOptionMapperData:

    def __init__(
            self,
            var_name: str,
            cmd_line_option: str,
            dflt_value: str = None):
        self.__var_name: str = var_name
        self.__cmd_line_option: str = cmd_line_option
        self.__dflt_value: str = dflt_value

    @property
    def var_name(self) -> str:
        return self.__var_name

    @property
    def dflt_value(self) -> str:
        return self.__dflt_value

    @property
    def cmd_line_option(self) -> str:
        return self.__cmd_line_option


class CommandLineOptionMapper(Enum):
    SQUEEZELITE_SERVER_PORT = CommandLineOptionMapperData(
        VariableName.SQUEEZELITE_SERVER_PORT.value,
        "-s")
    SQUEEZELITE_AUDIO_DEVICE = CommandLineOptionMapperData(
        VariableName.SQUEEZELITE_AUDIO_DEVICE.value,
        "-o")

    @property
    def var_name(self) -> str:
        return self.value.var_name

    @property
    def dflt_value(self) -> str:
        return self.value.dflt_value

    @property
    def cmd_line_option(self) -> str:
        return self.value.cmd_line_option


def add_command_line_option(
        command_line: str,
        mapper: CommandLineOptionMapper) -> str:
    v: str = os.getenv(mapper.var_name, mapper.dflt_value)
    if v:
        print(f"Using [{v}] for parameter [{mapper.cmd_line_option}] ...")
        command_line = f"{command_line} {mapper.cmd_line_option} {v}"
    return command_line


def main():
    fallback_sq_binary: str = "squeezelite"
    sq_default_binary: Path = Path("/usr/bin/squeezelite")
    if sq_default_binary.is_file():
        # file exists
        fallback_sq_binary = sq_default_binary.resolve(strict=True)
    sq_binary: str = os.getenv("SQUEEZELITE_BINARY", fallback_sq_binary)
    print(f"squeezelite runner is using [{sq_binary}]")
    command_line: str = sq_binary
    command_line = add_command_line_option(
        command_line=command_line,
        mapper=CommandLineOptionMapper.SQUEEZELITE_SERVER_PORT)
    command_line = add_command_line_option(
        command_line=command_line,
        mapper=CommandLineOptionMapper.SQUEEZELITE_AUDIO_DEVICE)
    print(f"Command line: [{command_line}]")
    os.system(command_line)


if __name__ == "__main__":
    main()
