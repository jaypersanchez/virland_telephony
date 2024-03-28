import speech_recognition as sr
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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
        return speech_text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

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
    details = listen_for_appointment()
    print(f"Appointment Details {details}")
    #if details:
        #create_calendar_event(details)
