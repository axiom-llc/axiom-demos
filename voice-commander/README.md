# AXIOM Voice Commander

AXIOM Voice Commander is a configurable, real-time local voice automation system that listens for spoken input, transcribes it offline, and executes predefined commands.

It complements AXIOM Voice Agent: Voice Agent handles cloud telephony and external callers, while Voice Commander provides offline workstation voice control.

## Features

- **Real-time transcription** via offline Vosk toolkit — no cloud dependency
- **Configurable static commands** — static commands defined in `commands.json`; dynamic command types are implemented in code
- **Portable paths** — `~` expansion supported in config
- **Static & dynamic commands** — simple mappings and stateful multi-step commands (e.g. `define this`)
- **Modular** — transcription and execution are separate components

## Prerequisites

Python 3 and a working microphone/audio input are required.

**Runtime system dependencies** (Arch Linux):
```bash
sudo pacman -S portaudio curl libnotify
```

`notify-send` is provided by `libnotify` and requires a running notification daemon.

**Setup helper** (Arch Linux):
```bash
sudo pacman -S unzip
```

**Vosk language model:**
```bash
mkdir -p ~/.config/vosk
unzip vosk-model-small-en-us-0.15.zip -d ~/.config/vosk/
```
Download from: https://alphacephei.com/vosk/models

## Setup

```bash
python3 -m pip install -r requirements.txt
cp commands.example.json commands.json
# Edit commands.json: set model_path and customize commands
```

## Usage

```bash
python3 main.py
python3 main.py --config /path/to/commands.json
```
