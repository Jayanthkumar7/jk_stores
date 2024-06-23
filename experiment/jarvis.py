import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser

def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            return ""
    return command.lower()

def respond(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def process_command(command):
    if 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        respond(f"The current time is {current_time}")
    elif 'open youtube' in command:
        webbrowser.open('https://www.youtube.com')
        respond("Opening YouTube")
    elif 'weather' in command:
        respond("I can provide weather updates if you integrate me with a weather API.")
    else:
        respond("Sorry, I don't know how to help with that.")

if __name__ == "__main__":
    while True:
        command = listen_command()
        if 'exit' in command:
            respond("Goodbye!")
            break
        if command:
            process_command(command)
