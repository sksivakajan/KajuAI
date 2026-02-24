import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 175)


def speak(text: str):
    print(f"KAJU AI: {text}")
    engine.say(text)
    engine.runAndWait()