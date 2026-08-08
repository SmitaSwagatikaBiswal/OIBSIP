import speech_recognition as sp
import pyttsx3 as pt
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

API_KEY = "07db125602deea9fb4784e31bc427581"
CITY = "Bhubaneswar"
MY_EMAIL = "mimilimiomio@gmail.com"
MY_PASSWORD = "woct dsgi mnpl jbdq"

engine = pt.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 170)

def speak(text):
    print(f"Assistant: {text}")
    try:
        time.sleep(1)
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        pass

def listen():
    rec = sp.Recognizer()
    with sp.Microphone() as source:
        print("Speak now. I am Listening...")
        rec.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = rec.listen(source, timeout=30, phrase_time_limit=5)
        except sp.WaitTimeoutError:
            return "none"
    try:
        query = rec.recognize_google(audio, language='en-in')
        return query.lower()
    except:
        return "none"
def answer_question(query):
    try:
        answer = wikipedia.summary(query, sentences=2)
        return answer
    except:
        webbrowser.open("https://www.google.com/search?q=" +urllib.parse.quote(query))
        return "I could not find an exact answer, so I opened Google."

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

def send_email(to, subject, content, sender_name):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(MY_EMAIL, MY_PASSWORD)
    server.sendmail(MY_EMAIL, to, f"Subject: {subject}\n\n{content}\n\nRegards, {sender_name}")
    server.close()

def set_reminder(seconds, message):
    def reminder_thread():
        time.sleep(seconds)
        speak(f"Reminder: {message}")
        winsound.Beep(1000, 2000)
    threading.Thread(target=reminder_thread).start()

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
    global current_voice_index
    global current_rate
    speak("Hello! I am your personal assistant.")
    speak("You can ask me about the time\n weather\n general knowledge\n set reminders\n  even send emails\n or even add custom command")
    
    while True:
        query = listen()
        if query == "none": continue

        if 'time' in query:
            speak(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}")
        
        elif 'weather' in query:
            print(get_weather())
            
        elif 'what is' in query or 'who is' in query or 'calculate' in query:
            speak("Searching....")
            speak(answer_question(query))
        
        elif 'send email' in query or 'email' in query or 'draft an email' in query or 'write an email' in query or 'send an email to' in query:
            try:
                speak("What is the subject of the email?")
                subject = listen()
                speak("What is the body of the email? (Please give a detailed message)")
                content = listen()
                speak("Whom should I send this email to?")
                recipient = listen()
                contacts = {
                    'mimili': 'mimilimiomio@gmail.com',
                    'me': MY_EMAIL,
                    'smita': 'smitaswagatikab@gmail.com'
                }

                Tmail = None
                if recipient and '@' in recipient:
                    Tmail = recipient
                else:
                    key = recipient.replace("@", "").strip().lower()
                    Tmail = contacts.get(key)

                if not Tmail:
                    speak("I don't have an email address for that recipient.")
                else:
                    send_email(Tmail, subject, content, "Assistant")
                speak("Email has been sent successfully.")
            except Exception as e:
                speak("I am sorry, I was unable to send the email.")

        elif "add command" in query:
            add_custom_command()

        elif 'reminder' in query:
            speak("What should I remind you about?")
            msg = listen()
            speak("After how much time in minutes?")
            mins = listen()
            try:
                val = int(''.join(filter(str.isdigit, mins)))
                set_reminder(val * 60, msg)
                speak(f"Reminder set for {val} minutes.")
            except: speak("Invalid time format.")

        elif 'exit' in query or 'stop' in query or 'quit' in query or 'bye' in query:
            speak("Okay, Bye! See you next time.")
            break
        else:
            speak("Please wait while I search the web.")
            webbrowser.open(f"https://www.google.com/search?q={query}")

if __name__ == "__main__":
    main()

