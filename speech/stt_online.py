import speech_recognition as sr


def listen_online():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening (online)...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio).lower().strip()
        print("You:", text)
        return text
    except sr.RequestError:
        return "__ONLINE_FAILED__"
    except:
        return ""