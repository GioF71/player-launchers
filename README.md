# player-launchers

Easily configure your players with environment variables, and launch them using Python.

- [Music Player Daemon](https://musicpd.org/)
- Squeezelite (player for [Lyrion Music Server](https://lyrion.org/))

## Caveat

This project is in the early development stages. Documentation might be incomplete or totally missing.  

## Players

### Squeezelite

The script is the file `sq-runner.py` in the `runner` directory of the repository.  
This one is currently very limited, and will support just a handful of environment variables.  

VARIABLE|DESCRIPTION
:---|:---
SQUEEZELITE_SERVER_PORT|The server and port, optional
SQUEEZELITE_AUDIO_DEVICE|The audio device, optional

#### Usage examples

Todo.

### MPD (Music Player Daemon)

The script is the file `mpd-runner.py` in the `runner` directory of the repository.  
The variables you can use are in the following table.

#### MPD Variables

VARIABLE|DESCRIPTION
:---|:---
MPD_BINARY_PATH|Where mpd is located, defaults to `/usr/bin/mpd`
CONFIG_FILE_NAME|Specifies where to write the configuration file. Not recommended to use
INSTANCE_NAME|Instance name for mpd, useful when you want to run more than one instance of mpd
CACHE_DIRECTORY|Specify where to locate the configuration directories for db, playlist, music, etc.
MPD_BIND_ADDRESS|Bind address, defaults to `[::]`. Multiple value can be provided, separated by a `,`
MPD_PORT|MPD listen port, defaults to `6600`
MUSIC_DIRECTORY|Where the music is located, optional
PLAYLIST_DIRECTORY|Where the playlists are located, optional
LOG_DIRECTORY|Where the logs are located, optional
CONFIG_DIRECTORY|Where the config files must be located, optional
ENABLE_DB_FILE|Enables the DB, defaults to `yes`
DB_FILE|Name for the DB file, defaults to `tag_cache`
LOG_LEVEL|Mpd log level, defaults to `notice`
ENABLE_LOG_FILE|Enables log file, defaults to `yes`
LOG_FILE_NAME|Log file name, defaults to `mpd.log`
PID_FILE|Pid file location, optional
ENABLE_STICKER_FILE|Enables the sticker file, defaults to `yes`
STICKER_FILE|Name of the sticker file, defaults to `sticker.sql`
ENABLE_STATE_FILE|Enables the state file, defaults to `yes`
STATE_FILE|Name of the state file, defaults to `state`
STATE_FILE_INTERVAL|Update interval, defaults to `15`
RESTORE_PAUSED|Restore mpd in paused state, defaults to `yes`
MPD_RUNNING_MODE|Set to `no-daemon`, `systemd` or `daemon`
MPD_RUN_WITH_STDERR|Run with `--stderr`
MPD_RUN_WITH_VERBOSE|Run with `--verbose`
INPUT_CURL_CREATE|Creates the curl input plugin entry, defaults to `yes`
INPUT_CURL_ENABLED|Enables curl input plugin, defaults to `yes`
DECODER_HDCD_CREATE|Creates the hdcd decoder plugin entry, defaults to `yes`
DECODER_HDCD_ENABLED|Enables hdcd decoder plugin, defaults to `yes`
DECODER_WILDMIDI_CREATE|Creates the wildmidi decoder plugin entry, defaults to `yes`
DECODER_WILDMIDI_ENABLED|Enables wildmidi decoder plugin, defaults to `no`
SAMPLERATE_CONVERTER|Sets `samplerate_converter`, example value is `soxr very high`
FILESYSTEM_CHARSET|Defaults to `UTF-8`
OUTPUT_CREATE|Indexed, create an output if set to `yes`
OUTPUT_ENABLED|Indexed, enables the output if set to `yes`
OUTPUT_TYPE|Indexed, specifies output type (valid values are `alsa`, `pipewire`, `pulse`, `null`, more to come)
OUTPUT_NAME|Indexed, specifies output name (automatically generated if not set)

Indexed variables can be added in multiple instances. For OUTPUT_CREATE, you can create the initial OUTPUT_CREATE, then OUTPUT_CREATE_1, OUTPUT_CREATE_2, etc.

##### Alsa Output

See the alsa-specific env variables:

VARIABLE|DESCRIPTION
:---|:---
OUTPUT_DEVICE|Output device, example: `hw:1,0`
OUTPUT_BUFFER_TIME|Output buffer time in microseconds
OUTPUT_PERIOD_TIME|Output period time in microseconds
OUTPUT_AUTO_RESAMPLE|Disables resampling if set to `no`
OUTPUT_AUTO_CHANNELS|Disables channel conversions if set to `no`
OUTPUT_AUTO_FORMAT|Disables sample format conversion if set to `no`
OUTPUT_DOP|Output property, valid for `alsa`
OUTPUT_STOP_DSD_SILENCE|Output property, valid for `alsa`
OUTPUT_THESYCON_DSD_WORKAROUND|Output property, valid for `alsa`
OUTPUT_ALLOWED_FORMATS|Output property, valid for `alsa`
OUTPUT_CLOSE_ON_PAUSE|Close the device while playback is paused, defaults to `yes`
OUTPUT_DEFAULT_FORMAT|Output default format, example `44100:16:2`
OUTPUT_MIXER_TYPE|Output mixer type, e.g. `software`
OUTPUT_MIXER_CONTROL|Mixer control
OUTPUT_MIXER_INDEX|Mixer index
OUTPUT_INTEGER_UPSAMPLING|Ouput property (only in my mpd branch), can be enabled with `yes`
OUTPUT_INTEGER_UPSAMPLING_ALLOWED|Ouput property (only in my mpd branch), specifies the formats that are subject to integer upsampling, example value: `44100:*:* 48000:*:*`

##### Pipewire Output

See the pipewire-specific env variables:

VARIABLE|DESCRIPTION
:---|:---
OUTPUT_TARGET|Output target
OUTPUT_REMOTE|Output remote
OUTPUT_DSD|Output dsd

##### PulseAudio Output

See the pulseaudio-specific env variables:

VARIABLE|DESCRIPTION
:---|:---
OUTPUT_HOSTNAME|Output hostname
OUTPUT_SINK|Output sink
OUTPUT_ROLE|Output role
OUTPUT_FACTOR|Output factor

##### Null Output

See the pulseaudio-specific env variables:

VARIABLE|DESCRIPTION
:---|:---
OUTPUT_SYNC|Output sync

#### Usage examples

##### User-level systemd unit

Create a text file, named e.g.: `mpd.env` with the following contents:

```text
MPD_RUNNING_MODE=systemd
INSTANCE_NAME=my-mpd-instance
OUTPUT_CREATE=yes
OUTPUT_TYPE=alsa
OUTPUT_DEVICE=hw:0
OUTPUT_MIXER_TYPE=software
```

Assuming that you save that file as `~/my-config/mpd.env` and that this repository is cloned at the directory `~/git/player-launchers`, create the user-level systemd unit with the following contents in `~/.config/systemd/user/my-mpd-instance.service` with the following contents:

```text
[Unit]
Description=My MPD instance
After=network.target network-online.target sound.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=%h/my-config/mpd.env
ExecStart=%h/git/player-launchers/runner/mpd-runner.py

[Install]
WantedBy=default.target
```

Reload systemd using:

```
systemctl --user daemon-reload
```

Start the service using:

```
systemctl --user start my-mpd-instance
```

This configuration will create an mpd instance with an alsa output for device `hw:0`.  

## Start services before login

You might want to enable login lingering for your user. Do this using:

```text
loginctl enable-linger $USER
```

## Dependencies

You just need to have Python installed.  

## Changelog

DATE|COMMENT
:---|:---
2025-04-30|First public release
