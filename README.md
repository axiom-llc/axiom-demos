# Voice Commander

A configurable, real-time voice command application that listens for spoken input, transcribes it to text, and executes predefined shell commands.

## Features

- **Real-time transcription** via offline Vosk toolkit — no cloud dependency
- **Fully configurable** — all commands defined in `commands.json`, no code edits needed
- **Portable paths** — `~` expansion supported in config
- **Static & dynamic commands** — simple mappings and stateful patterns (e.g. `define this <word>`)
- **Modular** — transcription and execution are separate components

## Prerequisites

**Vosk language model:**
```bash
mkdir -p ~/.config/vosk
unzip vosk-model-small-en-us-0.15.zip -d ~/.config/vosk/
```
Download from: https://alphacephei.com/vosk/models

**System dependency** (Arch Linux):
```bash
sudo pacman -S portaudio
```

## Setup

```bash
pip install -r requirements.txt
cp commands.example.json commands.json
# Edit commands.json: set model_path and customize commands
```

## Usage

```bash
python main.py
python main.py --config /path/to/commands.json
```
