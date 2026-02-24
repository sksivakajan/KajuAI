# KajuAI

KajuAI is a Windows voice assistant that can:
- Listen in online, offline, or auto mode
- Speak replies using text-to-speech
- Run local actions like opening apps/folders, search, WhatsApp message flow, lock, restart, and shutdown
- Handle normal chat using OpenAI when a command is not detected

## Features
- Voice input:
  - Online: Google Speech Recognition (`speech_recognition`)
  - Offline: Vosk local model (`model/`)
  - Auto fallback between online and offline
- Voice output: `pyttsx3`
- Action parser for commands like:
  - `open chrome`
  - `search weather today`
  - `send whatsapp to 9477xxxxxxx hello`
  - `time`, `date`, `lock`, `restart`, `shutdown`
- Chat mode powered by OpenAI API (`chatgpt_brain.py`)

## Requirements
- Windows 10/11
- Python 3.10+
- Microphone
- Internet connection for online speech mode and OpenAI chat

## Installation
1. Clone the repository:
```bash
git clone https://github.com/sksivakajan/KajuAI.git
cd KajuAI
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set your OpenAI API key (PowerShell):
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

## Configuration
Edit `config.py`:
- `MODE`: `"online"`, `"offline"`, or `"auto"`
- `APPS`: map app names to executable paths on your PC
- `VOSK_MODEL_PATH`: path to your offline Vosk model (default `model`)

Example:
```python
MODE = "auto"
APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": r"C:\Users\VICTUS\AppData\Local\Programs\Microsoft VS Code\Code.exe",
}
VOSK_MODEL_PATH = "model"
```

## Run
```bash
python assistant.py
```

You can also use:
```bash
scripts\start_kaju_ai.bat
```

## Command Examples
- `open chrome`
- `open documents then search github copilot`
- `send whatsapp to 9477xxxxxxx hello`
- `what time is it`
- `what is today's date`
- `exit`

## Project Structure
- `assistant.py` - main loop, routing between commands and chat
- `commands.py` - command parsing and system actions
- `chatgpt_brain.py` - OpenAI chat logic
- `speech/` - speech-to-text and text-to-speech modules
- `config.py` - app settings and paths
- `model/` - offline STT model assets

## Notes
- Shutdown/restart/lock commands are active and execute system actions immediately.
- If an app is not found, add or fix its path in `config.py`.
- For WhatsApp name-based messaging, populate `CONTACTS` in `commands.py`.

## License
See [LICENSE](LICENSE).