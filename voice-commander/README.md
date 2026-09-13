# AXIOM Voice Commander demo

Local workstation voice-automation example. Vosk transcribes microphone audio
offline and the executor matches configured phrases to commands. It complements
the cloud-telephony Voice Agent, but has a materially different boundary: it can
execute commands on the local workstation.

## Requirements

Python 3, a working microphone, PortAudio support, and a downloaded Vosk model
are required. The included commands target an Arch Linux desktop; install its
runtime dependencies there, or adapt the configuration for another platform:

```bash
sudo pacman -S portaudio curl libnotify unzip
```

Download `vosk-model-small-en-us-0.15` from the
[Vosk model catalog](https://alphacephei.com/vosk/models), then extract it at
the path used by your configuration, for example:

```bash
mkdir -p ~/.config/vosk
unzip vosk-model-small-en-us-0.15.zip -d ~/.config/vosk/
```

## Configure and run

```bash
python3 -m pip install -r requirements.txt
cp commands.example.json commands.json
python3 main.py
```

Edit `commands.json` before running. It must contain `settings` with
`model_path`, `target_sample_rate`, `device_id`, and `buffer_size`, plus
`commands`. `~` is expanded in configured model and project-manager paths.
Choose a different file with `python3 main.py --config /path/to/commands.json`.

## Execution boundary

Static commands require exact transcript matches and are executed as shell
strings from the local configuration. Treat that configuration as trusted code:
a person with write access to it can cause arbitrary local commands to run.

The `project start <name>` path passes the spoken project name as an argument
vector; the definition lookup and notification paths also use argument vectors.
The `project stop` mapping remains a configured shell command. No fuzzy or
prefix matching is used for static commands. Network access is required only for
the optional `define this` lookup through `dict.org`; Vosk transcription itself
is offline.

This demo has no privilege separation, confirmation prompt, command allowlist
beyond its local configuration, sandbox, or audit trail. Do not use an
unreviewed configuration or treat it as a security boundary.

## Validation

The repository includes hardware-independent tests for configuration,
transcription flow, and command execution boundaries:

```bash
python -m unittest -v test_config.py test_executor.py test_transcriber.py
```

Portfolio CI runs those tests on Python 3.11 and 3.12. It does not test an
actual microphone, installed desktop commands, the Vosk model, or dict.org.
