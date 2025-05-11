#!/usr/bin/env python3

import os
import pathlib
import subprocess

from typing import Callable
from enum import Enum

import exceptions


class RequiredVariable(Exception):
    pass


class RootUserNotSupported(Exception):
    pass


class MustBeDirectory(Exception):
    pass


class NoHomePath(Exception):
    pass


class NotAnOutputType(Exception):
    pass


class NotARunningMode(Exception):
    pass


class _FunctionProxy:
    """Allow to mask a function as an Object."""
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


class EnvironmentVariableData:

    def __init__(
            self,
            indexed: bool = False,
            default_value: str = None,
            mpd_conf_key: str = None,
            validator: Callable[[str], str] = None):
        self.__indexed: bool = indexed
        self.__default_value: str = default_value
        self.__mpd_conf_key: str = mpd_conf_key
        self.__validator: Callable[[str], str] = validator

    @property
    def indexed(self) -> bool:
        return self.__indexed

    @property
    def default_value(self) -> str:
        return self.__default_value

    @property
    def mpd_conf_key(self) -> str:
        return self.__mpd_conf_key

    @property
    def validator(self) -> Callable[[str], str]:
        return self.__validator


class IndexedEnvironmentVariableData(EnvironmentVariableData):

    def __init__(
            self,
            default_value: str = None,
            mpd_conf_key: str = None,
            validator: Callable[[str], str] = None):
        super().__init__(
            indexed=True,
            default_value=default_value,
            mpd_conf_key=mpd_conf_key,
            validator=validator)


class Validator(Enum):
    MUST_BE_INT = _FunctionProxy(lambda x: must_be_int(x))
    YES_NO_OR_EMPTY = _FunctionProxy(lambda x: yes_no_or_empty(x))
    MUST_BE_OUTPUT_TYPE = _FunctionProxy(lambda x: must_be_output_type(x))
    MUST_BE_RUNNING_MODE = _FunctionProxy(lambda x: must_be_running_mode(x))


class MpdRunningModeData:

    def __init__(
            self,
            mode_name: str,
            command_line_switch: str = None):
        self.__mode_name: str = mode_name
        self.__command_line_switch: str = command_line_switch

    @property
    def mode_name(self) -> str:
        return self.__mode_name

    @property
    def command_line_switch(self) -> str:
        return self.__command_line_switch


class MpdRunningMode(Enum):
    NO_DAEMON = MpdRunningModeData("no-daemon", "--no-daemon")
    SYSTEMD = MpdRunningModeData("systemd", "--systemd")
    DAEMON = MpdRunningModeData("daemon", "")

    @property
    def mode_name(self) -> str:
        return self.value.mode_name

    @property
    def command_line_switch(self) -> str:
        return self.value.command_line_switch


class MpdConfKey(Enum):
    MUSIC_DIRECTORY = "music_directory"
    PLAYLIST_DIRECTORY = "playlist_directory"
    DB_FILE = "db_file"
    STICKER_FILE = "sticker_file"
    STATE_FILE = "state_file"
    STATE_FILE_INTERVAL = "state_file_interval"
    RESTORE_PAUSED = "restore_paused"
    LOG_FILE = "log_file"
    LOG_LEVEL = "log_level"
    PID_FILE = "pid_file"
    BIND_TO_ADDRESS = "bind_to_address"
    PORT = "port"
    SAMPLERATE_CONVERTER = "samplerate_converter"
    FILESYSTEM_CHARSET = "filesystem_charset"
    OUTPUT_NAME = "name"
    OUTPUT_ENABLED = "enabled"
    OUTPUT_DEVICE = "device"
    OUTPUT_MIXER_TYPE = "mixer_type"
    OUTPUT_TARGET = "target"
    OUTPUT_REMOTE = "remote"
    OUTPUT_DSD = "dsd"
    OUTPUT_BUFFER_TIME = "buffer_time"
    OUTPUT_PERIOD_TIME = "period_time"
    OUTPUT_CLOSE_ON_PAUSE = "close_on_pause"
    OUTPUT_DEFAULT_FORMAT = "default_format"
    OUTPUT_AUTO_RESAMPLE = "auto_resample"
    OUTPUT_AUTO_CHANNELS = "auto_channels"
    OUTPUT_AUTO_FORMAT = "auto_format"
    OUTPUT_THESYCON_DSD_WORKAROUND = "thesycon_dsd_workaround"
    OUTPUT_FORMAT = "format"
    OUTPUT_DOP = "dop"
    OUTPUT_ALLOWED_FORMATS = "allowed_formats"
    OUTPUT_MIXER_INDEX = "mixer_index"
    OUTPUT_MIXER_CONTROL = "mixer_control"
    OUTPUT_STOP_DSD_SILENCE = "stop_dsd_silence"
    OUTPUT_HOSTNAME = "hostname"
    OUTPUT_SINK = "sink"
    OUTPUT_MEDIA_ROLE = "media_role"
    OUTPUT_SCALE_FACTOR = "scale_factor"
    OUTPUT_SYNC = "sync"
    OUTPUT_INTEGER_UPSAMPLING = "integer_upsampling"
    OUTPUT_INTEGER_UPSAMPLING_ALLOWED = "integer_upsampling_allowed"
    OUTPUT_PORT = "port"
    OUTPUT_BIND_TO_ADDRESS = "bind_to_address"
    OUTPUT_DSCP_CLASS = "dscp_class"
    OUTPUT_ENCODER = "encoder"
    OUTPUT_BITRATE = "bitrate"
    OUTPUT_QUALITY = "quality"
    OUTPUT_MAX_CLIENTS = "max_clients"
    OUTPUT_GENRE = "genre"
    OUTPUT_WEBSITE = "website"
    OUTPUT_ALWAYS_ON = "always_on"


class EnvironmentVariable(Enum):
    CONFIG_FILE_NAME = EnvironmentVariableData(default_value="mpd.conf")
    INSTANCE_NAME = EnvironmentVariableData(default_value="mpd-default")
    CACHE_DIRECTORY = EnvironmentVariableData()
    MPD_BINARY_PATH = EnvironmentVariableData(default_value="/usr/bin/mpd")
    MPD_BIND_ADDRESS = EnvironmentVariableData(default_value="[::]")
    MPD_PORT = EnvironmentVariableData(
        default_value="6600",
        validator=Validator.MUST_BE_INT.value,
        mpd_conf_key=MpdConfKey.PORT.value)
    MUSIC_DIRECTORY = EnvironmentVariableData()
    PLAYLIST_DIRECTORY = EnvironmentVariableData()
    LOG_DIRECTORY = EnvironmentVariableData()
    CONFIG_DIRECTORY = EnvironmentVariableData()
    ENABLE_DB_FILE = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value)
    DB_FILE = EnvironmentVariableData(default_value="tag_cache")
    LOG_LEVEL = EnvironmentVariableData(
        default_value="notice",
        mpd_conf_key=MpdConfKey.LOG_LEVEL.value)
    ENABLE_LOG_FILE = EnvironmentVariableData(default_value="yes")
    LOG_FILE_NAME = EnvironmentVariableData(default_value="mpd.log")
    PID_FILE = EnvironmentVariableData(mpd_conf_key=MpdConfKey.PID_FILE.value)
    ENABLE_STICKER_FILE = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value)
    STICKER_FILE = EnvironmentVariableData(
        default_value="sticker.sql",
        mpd_conf_key=MpdConfKey.STICKER_FILE.value)
    ENABLE_STATE_FILE = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value)
    STATE_FILE = EnvironmentVariableData(
        default_value="state",
        mpd_conf_key=MpdConfKey.STATE_FILE.value)
    STATE_FILE_INTERVAL = EnvironmentVariableData(
        default_value="15",
        mpd_conf_key=MpdConfKey.STATE_FILE_INTERVAL.value)
    RESTORE_PAUSED = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value,
        mpd_conf_key=MpdConfKey.RESTORE_PAUSED.value)
    # curl is mandatory for streaming
    INPUT_CURL_CREATE = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value)
    INPUT_CURL_ENABLED = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value)
    SAMPLERATE_CONVERTER = EnvironmentVariableData(mpd_conf_key=MpdConfKey.SAMPLERATE_CONVERTER.value)
    # opus decoder, might have issues for streaming,
    # so we disable it by default (ffmpeg should replace its functionality)
    DECODER_OPUS_CREATE = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value)
    DECODER_OPUS_ENABLED = EnvironmentVariableData(
        default_value="no",
        validator=Validator.YES_NO_OR_EMPTY.value)
    DECODER_FFMPEG_CREATE = EnvironmentVariableData(
        default_value="no",
        validator=Validator.YES_NO_OR_EMPTY.value)
    DECODER_FFMPEG_ENABLED = EnvironmentVariableData(
        default_value="no",
        validator=Validator.YES_NO_OR_EMPTY.value)
    # hdcd support, enabled by default
    DECODER_HDCD_CREATE = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value)
    DECODER_HDCD_ENABLED = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value)
    # wildmini support, dissbled by default
    DECODER_WILDMIDI_CREATE = EnvironmentVariableData(
        default_value="yes",
        validator=Validator.YES_NO_OR_EMPTY.value)
    DECODER_WILDMIDI_ENABLED = EnvironmentVariableData(
        default_value="no",
        validator=Validator.YES_NO_OR_EMPTY.value)
    # other stuff
    FILESYSTEM_CHARSET = EnvironmentVariableData(
        default_value="UTF-8",
        mpd_conf_key=MpdConfKey.FILESYSTEM_CHARSET.value)
    MPD_RUNNING_MODE = EnvironmentVariableData(
        default_value="no-daemon",
        validator=Validator.MUST_BE_RUNNING_MODE.value)
    MPD_RUN_WITH_STDERR = EnvironmentVariableData(
        default_value="no",
        validator=Validator.YES_NO_OR_EMPTY.value)
    MPD_RUN_WITH_VERBOSE = EnvironmentVariableData(
        default_value="no",
        validator=Validator.YES_NO_OR_EMPTY.value)
    # outputs
    OUTPUT_CREATE = IndexedEnvironmentVariableData()
    # most likely people will want to create an alsa output
    OUTPUT_TYPE = IndexedEnvironmentVariableData(default_value="alsa")
    # common
    OUTPUT_ENABLED = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_ENABLED.value)
    OUTPUT_NAME = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_NAME.value)
    OUTPUT_MIXER_TYPE = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_MIXER_TYPE.value)
    OUTPUT_FORMAT = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_FORMAT.value)
    # alsa
    OUTPUT_DEVICE = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_DEVICE.value)
    OUTPUT_MIXER_CONTROL = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_MIXER_CONTROL.value)
    OUTPUT_MIXER_INDEX = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_MIXER_INDEX)
    OUTPUT_ALLOWED_FORMATS = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_ALLOWED_FORMATS.value)
    OUTPUT_AUTO_RESAMPLE = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_AUTO_RESAMPLE.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    OUTPUT_AUTO_CHANNELS = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_AUTO_CHANNELS.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    OUTPUT_AUTO_FORMAT = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_AUTO_FORMAT.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    OUTPUT_BUFFER_TIME = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_BUFFER_TIME.value)
    OUTPUT_CLOSE_ON_PAUSE = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_CLOSE_ON_PAUSE.value)
    OUTPUT_PERIOD_TIME = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_PERIOD_TIME.value)
    OUTPUT_DEFAULT_FORMAT = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_DEFAULT_FORMAT.value)
    OUTPUT_STOP_DSD_SILENCE = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_STOP_DSD_SILENCE.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    OUTPUT_THESYCON_DSD_WORKAROUND = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_THESYCON_DSD_WORKAROUND.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    OUTPUT_DOP = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_DOP.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    OUTPUT_INTEGER_UPSAMPLING = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_INTEGER_UPSAMPLING.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    OUTPUT_INTEGER_UPSAMPLING_ALLOWED = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_INTEGER_UPSAMPLING_ALLOWED.value)
    # pipewire
    OUTPUT_TARGET = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_TARGET.value)
    OUTPUT_REMOTE = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_REMOTE.value)
    OUTPUT_DSD = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_DSD.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    OUTPUT_HOSTNAME = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_HOSTNAME.value)
    OUTPUT_SINK = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_SINK.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    OUTPUT_MEDIA_ROLE = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_MEDIA_ROLE.value)
    OUTPUT_SCALE_FACTOR = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_SCALE_FACTOR.value)
    OUTPUT_SYNC = IndexedEnvironmentVariableData(
        mpd_conf_key=MpdConfKey.OUTPUT_SYNC.value,
        validator=Validator.YES_NO_OR_EMPTY.value)
    # httpd
    OUTPUT_PORT = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_PORT.value)
    OUTPUT_BIND_TO_ADDRESS = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_BIND_TO_ADDRESS.value)
    OUTPUT_DSCP_CLASS = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_DSCP_CLASS.value)
    OUTPUT_ENCODER = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_ENCODER.value, default_value="lame")
    OUTPUT_BITRATE = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_BITRATE.value)
    OUTPUT_QUALITY = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_QUALITY.value)
    OUTPUT_MAX_CLIENTS = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_MAX_CLIENTS.value)
    OUTPUT_GENRE = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_GENRE.value)
    OUTPUT_WEBSITE = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_WEBSITE.value, default_value="yes")
    OUTPUT_ALWAYS_ON = IndexedEnvironmentVariableData(mpd_conf_key=MpdConfKey.OUTPUT_ALWAYS_ON.value)

    @property
    def indexed(self) -> bool:
        return self.value.indexed

    @property
    def default_value(self) -> str:
        return self.value.default_value

    @property
    def mpd_conf_key(self) -> str:
        return self.value.mpd_conf_key

    @property
    def validator(self) -> Callable[[str], str]:
        return self.value.validator


class OutputPropertyData:

    def __init__(self, env_var: EnvironmentVariable):
        self.__env_var: EnvironmentVariable = env_var

    @property
    def env_var(self) -> EnvironmentVariable:
        return self.__env_var


class OutputProperty(Enum):

    @property
    def env_var(self) -> EnvironmentVariable:
        return self.value.env_var


class AlsaOutputProperty(OutputProperty):
    OUTPUT_DEVICE = OutputPropertyData(EnvironmentVariable.OUTPUT_DEVICE)
    OUTPUT_MIXER_TYPE = OutputPropertyData(EnvironmentVariable.OUTPUT_MIXER_TYPE)
    OUTPUT_MIXER_CONTROL = OutputPropertyData(EnvironmentVariable.OUTPUT_MIXER_CONTROL)
    OUTPUT_MIXER_INDEX = OutputPropertyData(EnvironmentVariable.OUTPUT_MIXER_INDEX)
    OUTPUT_ALLOWED_FORMATS = OutputPropertyData(EnvironmentVariable.OUTPUT_ALLOWED_FORMATS)
    OUTPUT_FORMAT = OutputPropertyData(EnvironmentVariable.OUTPUT_FORMAT)
    OUTPUT_AUTO_RESAMPLE = OutputPropertyData(EnvironmentVariable.OUTPUT_AUTO_RESAMPLE)
    OUTPUT_AUTO_CHANNELS = OutputPropertyData(EnvironmentVariable.OUTPUT_AUTO_CHANNELS)
    OUTPUT_AUTO_FORMAT = OutputPropertyData(EnvironmentVariable.OUTPUT_AUTO_FORMAT)
    OUTPUT_BUFFER_TIME = OutputPropertyData(EnvironmentVariable.OUTPUT_BUFFER_TIME)
    OUTPUT_PERIOD_TIME = OutputPropertyData(EnvironmentVariable.OUTPUT_PERIOD_TIME)
    OUTPUT_CLOSE_ON_PAUSE = OutputPropertyData(EnvironmentVariable.OUTPUT_CLOSE_ON_PAUSE)
    OUTPUT_DEFAULT_FORMAT = OutputPropertyData(EnvironmentVariable.OUTPUT_DEFAULT_FORMAT)
    OUTPUT_STOP_DSD_SILENCE = OutputPropertyData(EnvironmentVariable.OUTPUT_STOP_DSD_SILENCE)
    OUTPUT_THESYCON_DSD_WORKAROUND = OutputPropertyData(EnvironmentVariable.OUTPUT_THESYCON_DSD_WORKAROUND)
    OUTPUT_DOP = OutputPropertyData(EnvironmentVariable.OUTPUT_DOP)
    OUTPUT_INTEGER_UPSAMPLING = OutputPropertyData(EnvironmentVariable.OUTPUT_INTEGER_UPSAMPLING)
    OUTPUT_INTEGER_UPSAMPLING_ALLOWED = OutputPropertyData(EnvironmentVariable.OUTPUT_INTEGER_UPSAMPLING_ALLOWED)


class PipewireOutputProperty(OutputProperty):
    OUTPUT_TARGET = OutputPropertyData(EnvironmentVariable.OUTPUT_TARGET)
    OUTPUT_REMOTE = OutputPropertyData(EnvironmentVariable.OUTPUT_REMOTE)
    OUTPUT_DSD = OutputPropertyData(EnvironmentVariable.OUTPUT_DSD)


class PulseOutputProperty(OutputProperty):
    OUTPUT_HOSTNAME = OutputPropertyData(EnvironmentVariable.OUTPUT_HOSTNAME)
    OUTPUT_SINK = OutputPropertyData(EnvironmentVariable.OUTPUT_SINK)
    OUTPUT_MEDIA_ROLE = OutputPropertyData(EnvironmentVariable.OUTPUT_MEDIA_ROLE)
    OUTPUT_SCALE_FACTOR = OutputPropertyData(EnvironmentVariable.OUTPUT_SCALE_FACTOR)


class HttpdOutputProperty(OutputProperty):
    OUTPUT_PORT = OutputPropertyData(EnvironmentVariable.OUTPUT_PORT)
    OUTPUT_BIND_TO_ADDRESS = OutputPropertyData(EnvironmentVariable.OUTPUT_BIND_TO_ADDRESS)
    OUTPUT_DSCP_CLASS = OutputPropertyData(EnvironmentVariable.OUTPUT_DSCP_CLASS)
    OUTPUT_FORMAT = OutputPropertyData(EnvironmentVariable.OUTPUT_FORMAT)
    OUTPUT_ENCODER = OutputPropertyData(EnvironmentVariable.OUTPUT_ENCODER)
    OUTPUT_BITRATE = OutputPropertyData(EnvironmentVariable.OUTPUT_BITRATE)
    OUTPUT_QUALITY = OutputPropertyData(EnvironmentVariable.OUTPUT_QUALITY)
    OUTPUT_MAX_CLIENTS = OutputPropertyData(EnvironmentVariable.OUTPUT_MAX_CLIENTS)
    OUTPUT_GENRE = OutputPropertyData(EnvironmentVariable.OUTPUT_GENRE)
    OUTPUT_WEBSITE = OutputPropertyData(EnvironmentVariable.OUTPUT_WEBSITE)
    OUTPUT_ALWAYS_ON = OutputPropertyData(EnvironmentVariable.OUTPUT_ALWAYS_ON)


class NullOutputProperty(OutputProperty):
    OUTPUT_SYNC = OutputPropertyData(EnvironmentVariable.OUTPUT_SYNC)


class OutputTypeData:

    def __init__(self, output_type_name: str, enum_type: type):
        self.__output_type_name: str = output_type_name
        self.__enum_type: type = enum_type

    @property
    def output_type_name(self) -> str:
        return self.__output_type_name

    @property
    def enum_type(self) -> type:
        return self.__enum_type


class OutputType(Enum):
    ALSA = OutputTypeData(output_type_name="alsa", enum_type=AlsaOutputProperty)
    PIPEWIRE = OutputTypeData(output_type_name="pipewire", enum_type=PipewireOutputProperty)
    PULSE = OutputTypeData(output_type_name="pulse", enum_type=PulseOutputProperty)
    NULL = OutputTypeData(output_type_name="null", enum_type=NullOutputProperty)
    HTTPD = OutputTypeData(output_type_name="httpd", enum_type=HttpdOutputProperty)

    @property
    def output_type_name(self) -> str:
        return self.value.output_type_name

    @property
    def enum_type(self) -> type:
        return self.value.enum_type


def get_output_properties_by_name(output_type_name: str) -> list[OutputProperty]:
    for ot in OutputType:
        if ot.output_type_name == output_type_name:
            enum_type: type = ot.enum_type
            return list(map(lambda x: x, enum_type))
    return None


def get_env_variable(env_var: EnvironmentVariable) -> str:
    v: str = os.getenv(env_var.name, env_var.default_value)
    if env_var.validator:
        v = env_var.validator(v)
    return v


def get_env_variable_as_bool(env_var: EnvironmentVariable) -> bool:
    return get_env_variable(env_var=env_var).lower() == "yes"


def get_indexed_env_variable(env_var: EnvironmentVariable, index: int = 0) -> bool:
    key: str = f"{env_var.name}{'_' + str(index) if index > 0 else ''}"
    v: str = os.getenv(key, env_var.default_value)
    if v and env_var.validator:
        v = env_var.validator(v)
    return v


def get_indexed_env_variable_as_bool(env_var: EnvironmentVariable, index: int = 0) -> bool:
    v: str = yes_no_or_empty(get_indexed_env_variable(env_var=env_var, index=index))
    return v and v.lower() == "yes"


def get_cache_directory() -> str:
    cache_dir: str = os.getenv(EnvironmentVariable.CACHE_DIRECTORY.name)
    cache_dir_path: pathlib.Path
    if not cache_dir:
        instance_name: str = get_env_variable(EnvironmentVariable.INSTANCE_NAME)
        if not instance_name:
            raise RequiredVariable("Instance name is required if cache directory is not specified")
        # fallback
        if os.getuid() != 0:
            home_path: pathlib.Path = pathlib.Path.home()
            if not home_path:
                raise NoHomePath("Cannot get home path")
            cache_dir_path = pathlib.Path.joinpath(home_path, ".cache", "mpd", instance_name)
        else:
            # what if we run as root?
            raise RootUserNotSupported("Cannot run as root")
    else:
        # use the specified cache directory
        cache_dir_path: pathlib.Path = pathlib.Path(os.path.expanduser(cache_dir))
    if not cache_dir_path.exists():
        # does not exist.
        print(f"Creating directory [{cache_dir_path}] ...")
        cache_dir_path.mkdir(parents=True)
        print(f"Created directory [{cache_dir_path}].")
    else:
        if not cache_dir_path.is_dir():
            print(f"Path [{cache_dir_path}] already exists, but it's not a directory")
            raise MustBeDirectory()
    return str(cache_dir_path.absolute())


def get_directory(env_var: EnvironmentVariable, fallback_cache_dir_name: str) -> str:
    the_dir: str = get_env_variable(env_var)
    if not the_dir:
        # not specified
        if os.getuid() != 0:
            # create a music dir inside cache dir
            cache_dir: str = get_cache_directory()
            music_dir_path = pathlib.Path.joinpath(pathlib.Path(cache_dir), fallback_cache_dir_name)
            # create if it does not exist
            if not music_dir_path.exists() or not music_dir_path.is_dir():
                # does not exist.
                print(f"Creating {fallback_cache_dir_name} directory [{music_dir_path}] ...")
                music_dir_path.mkdir(parents=True)
                print(f"Created {fallback_cache_dir_name} directory [{music_dir_path}].")
        else:
            # what if we run as root?
            raise RootUserNotSupported("Cannot run as root")
        return str(music_dir_path.absolute())
    else:
        # does the specified directory exist?
        specified_music_path: pathlib.Path = pathlib.Path(os.path.expanduser(the_dir))
        if not specified_music_path.exists():
            # create
            print(f"Creating directory [{specified_music_path}] ...")
            specified_music_path.mkdir(parents=True)
            print(f"Created directory [{specified_music_path}].")
        else:
            if not specified_music_path.is_dir():
                print(f"Path [{specified_music_path}] already exists, but it's not a directory")
                raise MustBeDirectory()
        return str(specified_music_path.absolute())


def get_music_directory() -> str:
    return get_directory(env_var=EnvironmentVariable.MUSIC_DIRECTORY, fallback_cache_dir_name="music")


def get_playlist_directory() -> str:
    return get_directory(env_var=EnvironmentVariable.PLAYLIST_DIRECTORY, fallback_cache_dir_name="playlist")


def get_config_directory() -> str:
    return get_directory(env_var=EnvironmentVariable.CONFIG_DIRECTORY, fallback_cache_dir_name="config")


def get_log_directory() -> str:
    return get_directory(env_var=EnvironmentVariable.LOG_DIRECTORY, fallback_cache_dir_name="log")


def get_log_file() -> str:
    if not get_env_variable_as_bool(env_var=EnvironmentVariable.ENABLE_LOG_FILE):
        return None
    log_file_name: str = get_env_variable(env_var=EnvironmentVariable.LOG_FILE_NAME)
    if log_file_name:
        return str(pathlib.Path(get_log_directory()).joinpath(log_file_name))
    return None


def get_db_file() -> str:
    if not get_env_variable_as_bool(env_var=EnvironmentVariable.ENABLE_DB_FILE):
        return None
    db_file: str = get_env_variable(env_var=EnvironmentVariable.DB_FILE)
    if db_file:
        return str(pathlib.Path(get_config_directory()).joinpath(db_file))
    return None


def get_sticker_file() -> str:
    if not get_env_variable_as_bool(env_var=EnvironmentVariable.ENABLE_STICKER_FILE):
        return None
    sticker_file: str = get_env_variable(env_var=EnvironmentVariable.STICKER_FILE)
    if sticker_file:
        return str(pathlib.Path(get_config_directory()).joinpath(sticker_file))
    return None


def get_state_file() -> str:
    if not get_env_variable_as_bool(env_var=EnvironmentVariable.ENABLE_STATE_FILE):
        return None
    sticker_file: str = get_env_variable(env_var=EnvironmentVariable.STATE_FILE)
    if sticker_file:
        return str(pathlib.Path(get_config_directory()).joinpath(sticker_file))
    return None


def get_state_file_interval() -> str:
    # relevant only if state file is specified
    if get_state_file():
        state_file_interval: str = get_env_variable(env_var=EnvironmentVariable.STATE_FILE_INTERVAL)
        return must_be_int(state_file_interval) if state_file_interval else None
    return None


def write_simple_value(f, key: str, value: str):
    f.write(f"{key} \"{value}\"\n")


def write_by_getter(f, getter: Callable[[], str], key_name: str):
    v: str = getter()
    if v:
        write_simple_value(f, key_name, v)


def write_variable(f, env_var: EnvironmentVariable):
    v: str = get_env_variable(env_var=env_var)
    if v:
        write_simple_value(f, env_var.mpd_conf_key, v)


def write_plugin(f, plugin_type: str, plugin_name: str, enabled: bool = True, properties: dict[str, str] = {}):
    f.write(f"{plugin_type} {{\n")
    f.write(f"  plugin \"{plugin_name}\"\n")
    f.write(f"  enabled \"{'yes' if enabled else 'no'}\"\n")
    for k, v in properties.items():
        f.write(f"  {k} \"{v}\"\n")
    f.write("}\n")


def write_input_plugin(f, plugin_name: str, enabled: bool = True, properties: dict[str, str] = {}):
    write_plugin(
        f=f,
        plugin_type="input",
        plugin_name=plugin_name,
        enabled=enabled,
        properties=properties)


def write_decoder_plugin(f, plugin_name: str, enabled: bool = True, properties: dict[str, str] = {}):
    write_plugin(
        f=f,
        plugin_type="decoder",
        plugin_name=plugin_name,
        enabled=enabled,
        properties=properties)


def write_simple_plugin(
        f,
        plugin_type: str,
        plugin_name: str,
        create: EnvironmentVariable,
        enabled: EnvironmentVariable,
        properties: dict[str, str] = {}):
    if get_env_variable_as_bool(env_var=create):
        write_plugin(
            f=f,
            plugin_type=plugin_type,
            plugin_name=plugin_name,
            enabled=get_env_variable_as_bool(env_var=enabled),
            properties=properties)


def write_output(
        f,
        output_type: str,
        properties: dict[str, str] = {}):
    f.write("audio_output {\n")
    f.write(f"  type \"{output_type}\"\n")
    for k, v in properties.items():
        f.write(f"  {k} \"{v}\"\n")
    f.write("}\n")


def write_config_file() -> str:
    config_dir: str = get_config_directory()
    config_file_name: str = get_env_variable(env_var=EnvironmentVariable.CONFIG_FILE_NAME)
    config_file: pathlib.Path = pathlib.Path(config_dir).joinpath(config_file_name)
    print(f"MPD config file name: [{config_file}]")
    with open(str(config_file), "w") as f:
        write_by_getter(f=f, getter=get_music_directory, key_name=MpdConfKey.MUSIC_DIRECTORY.value)
        write_by_getter(f=f, getter=get_playlist_directory, key_name=MpdConfKey.PLAYLIST_DIRECTORY.value)
        write_by_getter(f=f, getter=get_db_file, key_name=MpdConfKey.DB_FILE.value)
        write_by_getter(f=f, getter=get_log_file, key_name=MpdConfKey.LOG_FILE.value)
        write_variable(f=f, env_var=EnvironmentVariable.PID_FILE)
        write_by_getter(f=f, getter=get_state_file, key_name=EnvironmentVariable.STATE_FILE.mpd_conf_key)
        write_by_getter(
            f=f,
            getter=get_state_file_interval,
            key_name=EnvironmentVariable.STATE_FILE_INTERVAL.mpd_conf_key)
        write_by_getter(
            f=f,
            getter=get_sticker_file,
            key_name=EnvironmentVariable.STICKER_FILE.mpd_conf_key)
        bind_addresses: str = get_env_variable(env_var=EnvironmentVariable.MPD_BIND_ADDRESS)
        if bind_addresses:
            # split by ","
            bind_address_list: list[str] = bind_addresses.split(",")
            bind_addr: str
            for bind_addr in bind_address_list:
                write_simple_value(
                    f=f,
                    key=MpdConfKey.BIND_TO_ADDRESS.value,
                    value=bind_addr.strip())
        write_variable(f=f, env_var=EnvironmentVariable.MPD_PORT)
        write_variable(f=f, env_var=EnvironmentVariable.LOG_LEVEL)
        write_variable(f=f, env_var=EnvironmentVariable.RESTORE_PAUSED)
        write_simple_plugin(
            f=f,
            plugin_type="input",
            plugin_name="curl",
            create=EnvironmentVariable.INPUT_CURL_CREATE,
            enabled=EnvironmentVariable.INPUT_CURL_ENABLED)
        write_simple_plugin(
            f=f,
            plugin_type="decoder",
            plugin_name="opus",
            create=EnvironmentVariable.DECODER_OPUS_CREATE,
            enabled=EnvironmentVariable.DECODER_OPUS_ENABLED)
        write_simple_plugin(
            f=f,
            plugin_type="decoder",
            plugin_name="ffmpeg",
            create=EnvironmentVariable.DECODER_FFMPEG_CREATE,
            enabled=EnvironmentVariable.DECODER_FFMPEG_ENABLED)
        write_simple_plugin(
            f=f,
            plugin_type="decoder",
            plugin_name="hdcd",
            create=EnvironmentVariable.DECODER_HDCD_CREATE,
            enabled=EnvironmentVariable.DECODER_HDCD_ENABLED)
        write_simple_plugin(
            f=f,
            plugin_type="decoder",
            plugin_name="wildmidi",
            create=EnvironmentVariable.DECODER_WILDMIDI_CREATE,
            enabled=EnvironmentVariable.DECODER_WILDMIDI_ENABLED)
        # outputs!
        max_outputs: int = 100
        for i in range(0, max_outputs):
            # output_is_set: str = get_indexed_env_variable(env_var=EnvironmentVariable.OUTPUT_CREATE, index=i)
            # if not output_is_set:
            #     break
            output_create: bool = get_indexed_env_variable_as_bool(env_var=EnvironmentVariable.OUTPUT_CREATE, index=i)
            # print(f"Output [{i}] must be created: [{'yes' if output_create is True else 'no'}]")
            if output_create:
                output_type: str = Validator.MUST_BE_OUTPUT_TYPE.value(get_indexed_env_variable(
                    env_var=EnvironmentVariable.OUTPUT_TYPE,
                    index=i))
                properties: dict[str, str] = {}
                # name is mandatory, so if it's not provided, we
                # generate a name based on the index i
                output_name: str = get_indexed_env_variable(env_var=EnvironmentVariable.OUTPUT_NAME, index=i)
                if not output_name:
                    output_name = f"output_{i}"
                properties[EnvironmentVariable.OUTPUT_NAME.mpd_conf_key] = output_name
                enabled: str = get_indexed_env_variable(env_var=EnvironmentVariable.OUTPUT_ENABLED, index=i)
                if enabled:
                    properties[EnvironmentVariable.OUTPUT_ENABLED.mpd_conf_key] = ("yes" if enabled.lower() == "yes"
                                                                                   else "no")
                property_list: list = get_output_properties_by_name(output_type)
                for p in property_list:
                    v: str = get_indexed_env_variable(env_var=p.env_var, index=i)
                    if v:
                        properties[p.env_var.mpd_conf_key] = v
                write_output(f=f, output_type=output_type, properties=properties)
        write_variable(f=f, env_var=EnvironmentVariable.SAMPLERATE_CONVERTER)
        write_variable(f=f, env_var=EnvironmentVariable.FILESYSTEM_CHARSET)
        f.close()
    return str(config_file)


def yes_no_or_empty(v: str) -> str:
    if not v or (v.lower() in ['yes', 'no']):
        return v
    raise exceptions.NotYesNoOrEmpty(f"Value [{v}] must be empty or one between 'yes' and 'no'")


def must_be_int(v: str) -> str:
    try:
        int_v: int = int(v)
        return str(int_v)
    except ValueError:
        raise exceptions.NotAnIntegerValue(f"Value [{v}] is not an integer")


def must_be_output_type(v: str) -> str:
    for ot in OutputType:
        if ot.value.output_type_name == v:
            return v
    raise NotAnOutputType(f"Value [{v}] is not an output type")


def must_be_running_mode(v: str) -> str:
    for ot in MpdRunningMode:
        if ot.value.mode_name == v:
            return v
    raise NotARunningMode(f"Value [{v}] is not a running mode")


def get_run_mode() -> MpdRunningMode:
    run_mode: str = get_env_variable(env_var=EnvironmentVariable.MPD_RUNNING_MODE)
    i: MpdRunningMode
    for i in MpdRunningMode:
        if i.value.mode_name == run_mode:
            return i
    raise NotARunningMode("Invalid mpd running mode")


def main():
    config_file: str = write_config_file()
    print(f"MPD config file name: [{config_file}]")
    subprocess.call(["cat", config_file])
    mpd_binary: str = get_env_variable(env_var=EnvironmentVariable.MPD_BINARY_PATH)
    print(f"MPD binary: [{mpd_binary}]")
    cmd_line_list: list[str] = [mpd_binary, config_file]
    mpd_running_mode: MpdRunningMode = get_run_mode()
    if mpd_running_mode and mpd_running_mode.command_line_switch:
        cmd_line_list.append(mpd_running_mode.command_line_switch)
    if get_env_variable_as_bool(env_var=EnvironmentVariable.MPD_RUN_WITH_STDERR):
        cmd_line_list.append("--stderr")
    if get_env_variable_as_bool(env_var=EnvironmentVariable.MPD_RUN_WITH_VERBOSE):
        cmd_line_list.append("--verbose")
    print(f"Command line: [{cmd_line_list}]")
    subprocess.call(cmd_line_list)


if __name__ == "__main__":
    main()
