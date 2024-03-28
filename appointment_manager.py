import speech_recognition as sr
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
from textblob import TextBlob

# Path to your credentials.json
CREDENTIALS_FILE_PATH = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']


def authenticate_google():
    """Authenticate and return Google Calendar API service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def analyze_intent(speech_text):
    """
    Analyzes the text to classify the intent and extract details like 'doctor's name'.
    """
    # Simple keyword matching for intent classification
    if "cancel" in speech_text:
        intent = "cancel_appointment"
    elif "reschedule" in speech_text:
        intent = "reschedule_appointment"
    else:
        intent = "schedule_appointment"

    # Basic entity extraction using regex (assuming a simple pattern for demonstration)
    doctor_match = re.search(r"doctor\s+([a-zA-Z]+)", speech_text)
    doctor_name = doctor_match.group(1) if doctor_match else "Unknown"
    
    return intent, doctor_name

def listen_for_appointment():
    """Listen for appointment details and return as text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say the appointment details after the beep... (e.g., 'Doctor's appointment on June 5th at 3 PM')")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        speech_text = r.recognize_google(audio)
        print("You said: " + speech_text)
        
        # Analyze the intent and extract details
        intent, doctor_name = analyze_intent(speech_text)
        print(f"Intent: {intent}, Doctor: {doctor_name}")
        return speech_text, intent, doctor_name

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    

def create_calendar_event(details):
    """Create an event in Google Calendar based on the details."""
    service = authenticate_google()
    # Parse 'details' to extract date and time, here we just use placeholders
    event_date = "2024-06-05"
    event_time_start = "15:00:00"
    event_time_end = "16:00:00"
    event = {
        'summary': details,
        'start': {'dateTime': f'{event_date}T{event_time_start}', 'timeZone': 'America/New_York'},
        'end': {'dateTime': f'{event_date}T{event_time_end}', 'timeZone': 'America/New_York'},
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")

if __name__ == "__main__":
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    # Start the timer
    start_time = time.time()
    speech_text, intent, doctor_name = listen_for_appointment()
    print(f"Extracted speech: {speech_text}, Intent: {intent}, Doctor: {doctor_name}")
    #if details:
        #create_calendar_event(details)
    # End the timer
    end_time = time.time()

    # Calculate and print the duration
    duration = end_time - start_time
    print(f"Execution Time: {duration} seconds")