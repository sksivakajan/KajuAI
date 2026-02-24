import os
import re
import webbrowser
import datetime
import urllib.parse
import subprocess
from pathlib import Path

from config import APPS
from speech.tts import speak


# Optional: map names -> phone numbers (Sri Lanka example: 9477xxxxxxx)
CONTACTS = {
    # "shalu": "94771234567",
    # "amma": "9477xxxxxxx",
}


def open_anything(target: str):
    t = target.lower().strip()

    # Folders
    if t in ["documents", "document", "docs"]:
        os.startfile(str(Path.home() / "Documents"))
        speak("Opening Documents")
        return
    if t in ["downloads", "download"]:
        os.startfile(str(Path.home() / "Downloads"))
        speak("Opening Downloads")
        return
    if t == "desktop":
        os.startfile(str(Path.home() / "Desktop"))
        speak("Opening Desktop")
        return

    # Windows 11 app: Phone Link
    if t in ["phone", "phone link", "phonelink"]:
        subprocess.run(["cmd", "/c", "start", "", "ms-phone:"], shell=False)
        speak("Opening Phone Link")
        return

    # Browsers (open via webbrowser if exe path missing)
    if t in ["chrome", "google chrome"]:
        candidates = [
            APPS.get("chrome"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
        ]
        for p in candidates:
            if p and os.path.exists(p):
                os.startfile(p)
                speak("Opening Chrome")
                return
        webbrowser.open("https://www.google.com")
        speak("Chrome not found. Opened default browser.")
        return

    if t in ["firefox", "mozilla firefox"]:
        candidates = [
            APPS.get("firefox"),
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ]
        for p in candidates:
            if p and os.path.exists(p):
                os.startfile(p)
                speak("Opening Firefox")
                return
        webbrowser.open("https://www.mozilla.org/firefox/")
        speak("Firefox not found. Opened download page.")
        return

    # Generic apps from config.py
    path = APPS.get(t)
    if path:
        os.startfile(path)
        speak(f"Opening {t}")
        return

    speak(f"I don't know '{target}'. Add it in config.py APPS or CONTACTS.")


def do_search(query: str):
    q = query.strip()
    if not q:
        speak("Tell me what to search.")
        return
    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(q)}")
    speak(f"Searching {q}")


def send_whatsapp(to_value: str, message: str):
    """
    Reliable method: send by phone number using wa.me link.
    You can also use CONTACTS mapping: 'shalu' -> '9477...'
    """
    to_value = to_value.strip().lower()
    msg = message.strip()

    if not msg:
        speak("What message should I send?")
        return

    # Resolve name -> number if available
    number = CONTACTS.get(to_value, to_value)

    # Keep only digits (allow +94 too)
    number_digits = re.sub(r"\D", "", number)

    # If user said a name not in CONTACTS, number_digits will be empty/short
    if len(number_digits) < 10:
        speak("For WhatsApp, say a phone number like 9477xxxxxxx, or add the name in CONTACTS.")
        return

    link = f"https://wa.me/{number_digits}?text={urllib.parse.quote(msg)}"
    webbrowser.open(link)
    speak("WhatsApp chat opened. Press send in WhatsApp.")


def smart_parse(sentence: str):
    """
    Turns one sentence into ordered actions.
    Supported patterns:
      - open <thing>
      - search <query>
      - send whatsapp to <name|number> <message>
      - time / date
      - shutdown / restart / lock / exit
    You can chain with: 'then', 'and then', ','.
    """
    s = " ".join(sentence.lower().strip().split())

    # Split into chunks for multi-step commands
    chunks = re.split(r"\bthen\b|,|;|\band then\b", s)
    chunks = [c.strip() for c in chunks if c.strip()]

    actions = []
    for c in chunks:
        # send whatsapp to X MESSAGE...
        m = re.search(r"send (?:a )?whatsapp (?:message )?to\s+(.+?)\s+(.+)$", c)
        if m:
            actions.append(("whatsapp", m.group(1), m.group(2)))
            continue

        # open X
        m = re.search(r"open\s+(.+)$", c)
        if m:
            actions.append(("open", m.group(1)))
            continue

        # search X
        m = re.search(r"search\s+(.+)$", c)
        if m:
            actions.append(("search", m.group(1)))
            continue

        # quick intents
        if "time" in c:
            actions.append(("time",))
            continue
        if "date" in c:
            actions.append(("date",))
            continue
        if "shutdown" in c or "shut down" in c:
            actions.append(("shutdown",))
            continue
        if "restart" in c:
            actions.append(("restart",))
            continue
        if "lock" in c:
            actions.append(("lock",))
            continue
        if c in ["exit", "quit", "stop"]:
            actions.append(("exit",))
            continue

        # If a chunk doesn't match, treat it as a search fallback
        actions.append(("search", c))

    return actions


def run_command(cmd: str):
    cmd = cmd.strip()
    if not cmd:
        return

    if cmd.lower().strip() in ["help", "commands"]:
        speak("Try: open firefox then search whatsapp then send whatsapp to 9477xxxxxxx hi. Also: time, date, lock, shutdown, restart, exit.")
        return

    actions = smart_parse(cmd)

    for a in actions:
        kind = a[0]

        if kind == "open":
            open_anything(a[1])

        elif kind == "search":
            do_search(a[1])

        elif kind == "whatsapp":
            send_whatsapp(a[1], a[2])

        elif kind == "time":
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {now}")

        elif kind == "date":
            today = datetime.datetime.now().strftime("%B %d, %Y")
            speak(f"Today is {today}")

        elif kind == "lock":
            speak("Locking computer.")
            os.system("rundll32.exe user32.dll,LockWorkStation")

        elif kind == "shutdown":
            speak("Shutting down.")
            os.system("shutdown /s /t 1")

        elif kind == "restart":
            speak("Restarting.")
            os.system("shutdown /r /t 1")

        elif kind == "exit":
            speak("Goodbye.")
            raise SystemExit

        else:
            speak("I didn't understand that part.")