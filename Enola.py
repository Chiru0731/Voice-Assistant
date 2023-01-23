from __future__ import print_function

import os
import os.path
import pickle
import sys
from datetime import date

import pyttsx3
import pyttsx3 as tts
import speech_recognition
import speech_recognition as sr
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from neuralintents import GenericAssistant

recognizer = speech_recognition.Recognizer()

speaker = tts.init()
speaker.setProperty('rate', 170)
voice = speaker.getProperty('voices')
speaker.setProperty('voice', voice[1].id)

todo_list = ['Go shopping', 'Clean room', 'Record video']


def new_note():
    global recognizer

    speaker.say("what do you want to write?")
    speaker.runAndWait()

    done = False

    while not done:
        try:

            with speech_recognition.Microphone() as mic:

                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic)

                note = recognizer.recognize_google(audio)
                note = note.lower()

                speaker.say('choose a filename!')
                speaker.runAndWait()

                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic)

                filename = recognizer.recognize_google(audio)
                filename = filename.lower()

                with open(f"{filename}.txt", 'w') as f:
                    f.write(note)
                    done = True
                    speaker.say(f"I successfully created the note{filename}")
                    speaker.runAndWait()

        except speech_recognition.UnknownValueError:
            recognizer = speech_recognition.Recognizer()
            speaker.say("Can you say it again!")


def add_todo():

    global recognizer

    speaker.say("what is to be added")
    speaker.runAndWait()

    done = False

    while not done:
        try:
            with speech_recognition.Microphone() as mic:

                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic)

                item = recognizer.recognize_google(audio)
                item = item.lower()

                todo_list.append(item)
                done = True

                speaker.say(f"New {item} has been added to to do list")
                speaker.runAndWait()

        except speech_recognition.UnknownValueError:
            recognizer = speech_recognition.Recognizer()
            speaker.say("i didn't under stand. can you say that again!")
            speaker.runAndWait()


def show_todo():

    speaker.say("the items on your to do list are ")
    for item in todo_list:
        speaker.say(item)
    speaker.runAndWait()


# If modifying these scopes, delete the file token.pickle .
# if you run this for the firs
# t time it will take you to gmail to choose your account
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    rate = engine.getProperty('rate')

    engine.setProperty('rate', rate - 20)

    engine.say(text)
    engine.runAndWait()


speak("Welcome to mail service")


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        said = ""

    try:
        said = r.recognize_google(audio)
        print(said)

    except:
        speak("Didn't get that")

    return said.lower()


def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None

    # The file token.pickle stores the user's
    # access and refresh tokens, and is
    # created automatically when the authorization
    # flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available,
    # let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def check_mails(service):
    # fetching emails of today's date
    today = (date.today())

    today_main = today.strftime('%Y/%m/%d')

    # Call the Gmail API
    results = service.users().messages().list(userId='me',
                                              labelIds=["INBOX", "UNREAD"],
                                              q="after:{0} and category:Primary".format(today_main)).execute()
    # The above code will get emails from primary
    # inbox which are unread
    messages = results.get('messages', [])

    if not messages:

        # if no new emails
        print('No messages found.')
        speak('No messages found.')
    else:
        m = ""

        # if email found
        speak("{} new emails found".format(len(messages)))

        speak("if you want to read any particular email just type read ")
        speak("and for not reading type leave ")
        for message in messages:

            msg = service.users().messages().get(userId='me',
                                                 id=message['id'], format='metadata').execute()

            for add in msg['payload']['headers']:
                if add['name'] == "From":

                    # fetching sender's email name
                    a = str(add['value'].split("<")[0])
                    print(a)

                    speak("email from" + a)
                    text = input()

                    if text == "read":

                        print(msg['snippet'])

                        # speak up the mail
                        speak(msg['snippet'])

                    else:
                        speak("email passed")


SERVICE2 = authenticate_gmail()
check_mails(SERVICE2)


def hello():
    speaker.say("hola!,what can i do for you?")
    speaker.runAndWait()


def quit():
    speaker.say("will be waiting!")
    speaker.runAndWait()
    sys.exit(0)


mappings = {
    "greeting": hello,
    "new_note": new_note,
    "add_todo": add_todo,
    "show_todo's": show_todo,
    "exit": quit
}

assistant = GenericAssistant('intents.json', intent_methods=mappings)
assistant.train_model()

assistant.save_model()
assistant.load_model()

while True:
    try:
        with speech_recognition.Microphone() as mic:

            recognizer.adjust_for_ambient_noise(mic, duration=0.2)
            audio = recognizer.listen(mic)

            message = recognizer.recognize_google(audio)
            message = message.lower()

        assistant.request(message)

    except speech_recognition.UnknownValueError:
        recognizer = speech_recognition.Recognizer()
