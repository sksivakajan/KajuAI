import os
import re
import webbrowser
import datetime
import urllib.parse
import subprocess
import time
import ctypes
from pathlib import Path

from config import APPS, LINKEDIN_PROFILE_URL
from speech.tts import speak

# Optional name -> phone mapping (Sri Lanka example: 9477xxxxxxx)
CONTACTS = {
    # "shalu": "94771234567",
}

KAJUAI_REPO_URL = "https://github.com/sksivakajan/KajuAI"
MUSIC_URL = "https://www.youtube.com/watch?v=55BS8QO5C9o&list=RDGMEMPipJmhsMq3GHGrfqf4WIqAVM55BS8QO5C9o&start_radio=1"
_LAST_ACTION_KEY = ""
_LAST_ACTION_AT = 0.0


def _is_duplicate_action(action_key: str, cooldown_sec: float = 2.5) -> bool:
    global _LAST_ACTION_KEY, _LAST_ACTION_AT
    now = time.time()
    if action_key == _LAST_ACTION_KEY and (now - _LAST_ACTION_AT) < cooldown_sec:
        return True
    _LAST_ACTION_KEY = action_key
    _LAST_ACTION_AT = now
    return False


# -------------------------
# Helpers
# -------------------------
def is_action_text(text: str) -> bool:
    t = (text or "").lower()
    if t.strip() == "ai":
        return True

    keywords = [
        "open ", "search ", "youtube", "send whatsapp", "send message",
        "shutdown", "restart", "lock", "time", "date", "linkedin",
        "play music", "stop it", "stop music", "pause music",
    ]
    return any(k in t for k in keywords)


def open_anything(target: str):
    t = target.lower().strip()

    # Folders
    if t in ["documents", "document", "docs"]:
        os.startfile(str(Path.home() / "Documents"))
        speak("Opening Documents")
        return True
    if t in ["downloads", "download"]:
        os.startfile(str(Path.home() / "Downloads"))
        speak("Opening Downloads")
        return True
    if t == "desktop":
        os.startfile(str(Path.home() / "Desktop"))
        speak("Opening Desktop")
        return True

    # Windows 11 Phone Link
    if t in ["phone", "phone link", "phonelink"]:
        subprocess.run(["cmd", "/c", "start", "", "ms-phone:"], shell=False)
        speak("Opening Phone Link")
        return True

    # Chrome
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
                return True
        webbrowser.open("https://www.google.com")
        speak("Chrome not found. Opened default browser.")
        return True

    # Firefox
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
                return True
        webbrowser.open("https://www.mozilla.org/firefox/")
        speak("Firefox not found. Opened download page.")
        return True

    # Other apps from config.py
    path = APPS.get(t)
    if path:
        try:
            os.startfile(path)
            speak(f"Opening {t}")
            return True
        except Exception:
            speak(f"Failed to open {t}. Check path in config.py")
            return True

    speak(f"I don't know '{target}'. Add it in config.py APPS or CONTACTS.")
    return True


def do_google_search(query: str):
    q = query.strip()
    if not q:
        speak("Tell me what to search.")
        return True
    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(q)}")
    speak(f"Searching {q}")
    return True


def do_youtube_search(query: str):
    q = query.strip()
    if not q:
        speak("Tell me what to play on YouTube.")
        return True
    webbrowser.open("https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q))
    speak(f"Opening YouTube for {q}")
    return True


def open_url_in_browser(url: str, browser_hint: str = ""):
    b = (browser_hint or "").lower().strip()

    if b in ["firefox", "firfox", "mozilla firefox"]:
        candidates = [
            APPS.get("firefox"),
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ]
        for p in candidates:
            if p and os.path.exists(p):
                subprocess.Popen([p, url], shell=False)
                speak("Opening in Firefox")
                return True

    webbrowser.open(url)
    speak("Opening link")
    return True


def open_linkedin_profile(browser_hint: str = ""):
    url = (LINKEDIN_PROFILE_URL or "").strip() or "https://www.linkedin.com/"
    if not (LINKEDIN_PROFILE_URL or "").strip():
        speak("LinkedIn profile URL is not set. Opening LinkedIn home.")
    return open_url_in_browser(url, browser_hint)


def stop_media_playback():
    # Windows media key: VK_MEDIA_STOP (0xB2)
    ctypes.windll.user32.keybd_event(0xB2, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0xB2, 0, 2, 0)
    speak("Stopped.")
    return True


def send_whatsapp(to_value: str, message: str):
    """
    Reliable: send using wa.me link.
    - to_value can be number like 9477xxxxxxx
    - or name if stored in CONTACTS
    """
    to_value = to_value.strip().lower()
    msg = message.strip()

    if not msg:
        speak("What message should I send?")
        return True

    number = CONTACTS.get(to_value, to_value)
    number_digits = re.sub(r"\D", "", number)

    if len(number_digits) < 10:
        speak("For WhatsApp, say a phone number like 9477xxxxxxx, or add the name in CONTACTS.")
        return True

    link = f"https://wa.me/{number_digits}?text={urllib.parse.quote(msg)}"
    webbrowser.open(link)
    speak("WhatsApp chat opened. Press send in WhatsApp.")
    return True


# -------------------------
# Smart parse -> actions
# -------------------------
def smart_parse(sentence: str):
    s = " ".join(sentence.lower().strip().split())

    # Break multi-step: "then", commas, etc.
    chunks = re.split(r"\bthen\b|,|;|\band then\b", s)
    chunks = [c.strip() for c in chunks if c.strip()]

    actions = []
    for c in chunks:
        # Fixed music command
        if c in ["play music", "play some music", "play music on youtube", "play some music on youtube"] or (
            "play" in c and "music" in c and "youtube" in c
        ):
            actions.append(("play_music",))
            continue

        if c in ["stop it", "stop music", "stop the music", "pause music", "pause it"]:
            actions.append(("stop_media",))
            continue

        # LinkedIn quick command
        if "linkedin" in c and ("open" in c or "go to" in c or "profile" in c):
            browser = "firefox" if ("firefox" in c or "firfox" in c) else ""
            actions.append(("linkedin_profile", browser))
            continue

        # Specific quick command for KajuAI repository
        if c in [
            "ai",
            "open ai",
            "open kajuai repo",
            "open kajuai repository",
            "open kaju ai repo",
            "open kaju repo",
            "kajuai repo",
            "kaju ai repo",
            "kaju repo",
        ]:
            actions.append(("open_url", KAJUAI_REPO_URL, "firefox"))
            continue

        # GitHub repo quick command:
        # "open my github in firefox go to the kajuai repository"
        if "github" in c and ("kajuai" in c or "kaju ai" in c):
            browser = "firefox" if ("firefox" in c or "firfox" in c) else ""
            actions.append(("open_url", KAJUAI_REPO_URL, browser))
            continue

        # WhatsApp: "send whatsapp to X MESSAGE..."
        m = re.search(r"send (?:a )?(?:whatsapp )?(?:message )?to\s+(.+?)\s+(.+)$", c)
        if m:
            actions.append(("whatsapp", m.group(1), m.group(2)))
            continue

        # YouTube play/search: "open youtube play tamil songs"
        m = re.search(r"(?:open\s+)?youtube.*(?:play|search)\s+(.+)$", c)
        if m:
            actions.append(("youtube_search", m.group(1)))
            continue

        # "open youtube"
        if c == "open youtube" or c == "youtube":
            actions.append(("youtube_home",))
            continue

        # open X
        m = re.search(r"open\s+(.+)$", c)
        if m:
            actions.append(("open", m.group(1)))
            continue

        # search X (google)
        m = re.search(r"search\s+(.+)$", c)
        if m:
            actions.append(("search", m.group(1)))
            continue

        # time/date/system
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

        # IMPORTANT CHANGE:
        # If it's not clearly an action, mark as unknown (do NOT auto-google-search)
        actions.append(("unknown", c))

    return actions


def run_actions_from_text(text: str) -> bool:
    """
    Returns True if any real action executed, False if it's basically chat.
    """
    actions = smart_parse(text)

    executed_any = False

    for a in actions:
        kind = a[0]

        if kind == "open":
            key = f"open:{a[1].strip().lower()}"
            if _is_duplicate_action(key):
                continue
            open_anything(a[1]); executed_any = True

        elif kind == "search":
            do_google_search(a[1]); executed_any = True

        elif kind == "youtube_search":
            key = f"youtube_search:{a[1].strip().lower()}"
            if _is_duplicate_action(key):
                continue
            do_youtube_search(a[1]); executed_any = True

        elif kind == "youtube_home":
            if _is_duplicate_action("youtube_home"):
                continue
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube")
            executed_any = True

        elif kind == "open_url":
            key = f"open_url:{a[1].strip().lower()}:{a[2].strip().lower()}"
            if _is_duplicate_action(key):
                continue
            open_url_in_browser(a[1], a[2]); executed_any = True

        elif kind == "linkedin_profile":
            key = f"linkedin_profile:{a[1].strip().lower()}"
            if _is_duplicate_action(key):
                continue
            open_linkedin_profile(a[1]); executed_any = True

        elif kind == "play_music":
            if _is_duplicate_action("play_music"):
                continue
            open_url_in_browser(MUSIC_URL, "firefox"); executed_any = True

        elif kind == "stop_media":
            if _is_duplicate_action("stop_media", cooldown_sec=1.0):
                continue
            stop_media_playback(); executed_any = True

        elif kind == "whatsapp":
            send_whatsapp(a[1], a[2]); executed_any = True

        elif kind == "time":
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {now}")
            executed_any = True

        elif kind == "date":
            today = datetime.datetime.now().strftime("%B %d, %Y")
            speak(f"Today is {today}")
            executed_any = True

        elif kind == "lock":
            speak("Locking computer.")
            os.system("rundll32.exe user32.dll,LockWorkStation")
            executed_any = True

        elif kind == "shutdown":
            speak("Shutting down.")
            os.system("shutdown /s /t 1")
            executed_any = True

        elif kind == "restart":
            speak("Restarting.")
            os.system("shutdown /r /t 1")
            executed_any = True

        elif kind == "exit":
            speak("Goodbye.")
            raise SystemExit

        elif kind == "unknown":
            # unknown means it's probably chat
            pass

    return executed_any
