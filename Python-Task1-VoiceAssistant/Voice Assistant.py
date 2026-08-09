import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import time
import smtplib
import requests
import threading
import winsound
import wikipedia
import urllib.parse
import json
import os
from email.message import EmailMessage

API_KEY = "07db125602deea9fb4784e31bc427581"
CITY = "Bhubaneswar"
MY_EMAIL = "mimilimiomio@gmail.com"
MY_PASSWORD = "woct dsgi mnpl jbdq"

engine = pyttsx3.init()
engine.setProperty("rate",170)
engine.setProperty("volume",1)
voices = engine.getProperty("voices")

if len(voices)>1:
    engine.setProperty("voice",voices[1].id)
def speak(text):
    print("Assistant :",text)
    engine.say(text)
    engine.runAndWait()

recognizer = sr.Recognizer()
def listen():
    with sr.Microphone() as source:
        recognizer.pause_threshold=1
        recognizer.energy_threshold=300
        recognizer.dynamic_energy_threshold=True
        recognizer.adjust_for_ambient_noise(source,1)
        print("\nListening...")
        try:
            audio=recognizer.listen(source,timeout=10,phrase_time_limit=12)
            print("Recognizing...")
            command = recognizer.recognize_google(audio)
            print("You :",command)
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand.")
            return ""
        except sr.WaitTimeoutError:
            speak("I didn't hear anything.")
            return ""
        except Exception as e:
            print(e)
            speak("Something went wrong.")
            return ""

def tell_time():
    current = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {current}")
    
def answer_question(query):
    try:
        answer = wikipedia.summary(query, sentences=2)
        return answer
    except:
        webbrowser.open("https://www.google.com/search?q=" +urllib.parse.quote(query))
        return "I could not find an exact answer, so I opened Google."

def google_search(query):
    url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    speak("Searching Google for " + query)
    webbrowser.open(url)
    
def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("cod") == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            return (f"The current temperature is {temp} degrees Celsius. "f"The weather is {desc}. "f"Humidity is {humidity} percent.")
        return "Sorry, I could not fetch the weather."
    except Exception as e:
        print(e)
        return "Unable to connect to the weather service."

def send_email():
    contacts = {
        "mimili": "mimilimiomio@gmail.com",
        "me": MY_EMAIL,
        "smita": "smitaswagatikab@gmail.com"}
    speak("Who should I send the email to?")
    recipient = listen().strip().lower()
    if recipient in contacts:
        email_address = contacts[recipient]
    elif "@" in recipient:
        email_address = recipient
    else:
        speak("Sorry, I don't know that contact.")
        return
    speak("What is the subject of the email?")
    subject = listen()
    if not subject:
        speak("I could not understand the subject.")
        return
    speak("What should I write in the email?")
    message = listen()
    if not message:
        speak("I could not understand the message.")
        return
    try:
        email = EmailMessage()
        email["From"] = MY_EMAIL
        email["To"] = email_address
        email["Subject"] = subject
        email.set_content(message)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MY_EMAIL, MY_PASSWORD)
        server.send_message(email)
        server.quit()
        speak("Email sent successfully.")
    except Exception as error:
        print("Email error:", error)
        speak("Sorry, I could not send the email.")

def set_reminder(seconds, message):
    def notify():
        speak("Reminder: " + message)
        winsound.Beep(1000, 2000)

    timer = threading.Timer(seconds, notify)
    timer.daemon = True
    timer.start()

if os.path.exists("commands.json"):
    with open("commands.json","r") as file:
        custom_commands = json.load(file)
else:
    custom_commands = {}
def execute_custom_command(query):
    for key, value in custom_commands.items():
        if key in query:
            speak("Opening " + key)
            webbrowser.open(value)
            return True
    return False
def add_custom_command():
    speak("What should the command be?")
    name = listen()
    speak("Say the website.")
    website = listen()
    website = website.replace(" ", "")
    if not website.startswith("http"):
        website = "https://" + website
    custom_commands[name] = website
    with open("commands.json","w") as file:
        json.dump(custom_commands,file,indent=4)
    speak("Command saved successfully.")

def main():
    speak("Hello! I am your personal assistant.")
    speak("I can tell you the time and weather, answer questions, send emails, "
          "set reminders, search Google, and open custom commands.")
    active = True
    while active:
        query = listen()
        if not query:
            continue
        exit_words = ["exit", "stop", "quit", "bye"]
        if any(word in query for word in exit_words):
            speak("Okay, Bye! See you next time.")
            active = False
            continue
        if execute_custom_command(query):
            continue
        if "time" in query:
            tell_time()
            continue
        if "weather" in query:
            speak(get_weather())
            continue
        if "email" in query:
            send_email()
            continue
        if "add command" in query:
            add_custom_command()
            continue
        if "reminder" in query:
            speak("What should I remind you about?")
            reminder_message = listen()
            if not reminder_message:
                speak("I could not understand the reminder.")
                continue
            speak("After how many minutes should I remind you?")
            reminder_time = listen()
            try:
                minutes = int(''.join(filter(str.isdigit, reminder_time)))
                if minutes <= 0:
                    speak("Please provide a positive number of minutes.")
                    continue
                set_reminder(minutes * 60, reminder_message)
                speak(f"Your reminder has been set for {minutes} minutes.")
            except (ValueError, TypeError):
                speak("Sorry, I could not understand the time.")
            continue
        question_words = ["what is", "who is", "calculate"]
        if any(word in query for word in question_words):
            speak("Searching for an answer.")
            answer = answer_question(query)
            speak(answer)
            continue
        google_search(query)
    speak("Assistant closed.")
if __name__ == "__main__":
    main()

