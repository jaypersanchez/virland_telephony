import speech_recognition as sr
import datetime
import pickle
import os.path
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import time
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

def get_embedding(text):
    # This function should return the embedding of the text
    # For this example, we'll pretend it returns a fixed vector
    #return np.random.rand(1, 768)  # Example embedding
    # Adjust this function to return the correct embedding size that matches your enriched_data.json
    return np.random.rand(1, 384)  # Adjusted to match Y.shape[1] == 384

def load_enriched_data():
    with open('assets/enriched_data.json', 'r') as file:
        return json.load(file)

def find_best_match(speech_text_embedding, enriched_data):
    max_similarity = -1
    best_match = None
    for item in enriched_data:
        # Ensure item_embedding is a 2D array; assuming item['vector'] is already a list
        item_embedding = np.array(item['vector']).reshape(1, -1)
        # Ensure speech_text_embedding is a 2D array
        speech_text_embedding_reshaped = speech_text_embedding.reshape(1, -1)
        similarity = cosine_similarity(speech_text_embedding_reshaped, item_embedding)[0][0]
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = item
    return best_match

def listen_for_appointment():
    """Listen for appointment details and use vector search to find the best match."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("How may we be of assistance?...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        speech_text = r.recognize_google(audio)
        print("You said: " + speech_text)
        
        # Get embedding for the recognized speech
        speech_text_embedding = get_embedding(speech_text)
        
        # Load enriched data
        enriched_data = load_enriched_data()
        
        # Find best match based on cosine similarity
        best_match = find_best_match(speech_text_embedding, enriched_data)
        if best_match:
            # Use 'intent' if available, otherwise fall back to 'request'
            match_key = 'intent' if 'intent' in best_match else 'request'
            print(f"Best match intent: {best_match[match_key]}")
            # Here you would continue with scheduling, cancelling, or rescheduling based on the intent
        else:
            print("No matching intent found.")
        
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")


# Example usage
if __name__ == "__main__":
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    # Start the timer
    start_time = time.time()
    listen_for_appointment()
    #if details:
        #create_calendar_event(details)
    # End the timer
    end_time = time.time()

    # Calculate and print the duration
    duration = end_time - start_time
    print(f"Execution Time: {duration} seconds")
