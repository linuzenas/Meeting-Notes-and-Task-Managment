import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
from transformers import pipeline
import re
import requests

# Trello API configuration
API_KEY = ''  # Replace with your actual API key
USER_TOKEN = ''  # Replace with your actual user token
BASE_URL = 'https://api.trello.com/1/'

def convert_audio_to_wav(input_file, output_file):
    audio_clip = AudioSegment.from_file(input_file)
    audio_clip.export(output_file, format='wav')

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(file_path)
    step = 10000  # 10 seconds in milliseconds
    chunks = make_chunks(audio, step)

    audio_segments = []

    for i, chunk in enumerate(chunks):
        chunk_file = f"chunk_{i}.wav"
        chunk.export(chunk_file, format="wav")

        with sr.AudioFile(chunk_file) as source:
            audio_data = recognizer.record(source)
            start_time = i * 10  # Start time in seconds
            try:
                text = recognizer.recognize_google(audio_data)
                audio_segments.append((start_time, text))
            except sr.UnknownValueError:
                audio_segments.append((start_time, "[Inaudible Segment]"))
            except sr.RequestError:
                return []
    return audio_segments

def summarize_text(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def extract_action_items(text):
    action_keywords = ["assign", "follow up", "send", "prepare", "complete"]
    pattern = r"\b(" + "|".join(action_keywords) + r")\b.*?\."
    actions = re.findall(pattern, text)
    return actions

def get_list_id_by_name(board_id, list_name):
    url = f'{BASE_URL}boards/{board_id}/lists'
    params = {
        'key': API_KEY,
        'token': USER_TOKEN
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        lists = response.json()
        for lst in lists:
            if lst['name'].lower() == list_name.lower():
                return lst['id']
        return None
    else:
        return None

def create_card_in_list(list_id, card_name, description=None):
    url = f'{BASE_URL}cards'
    params = {
        'key': API_KEY,
        'token': USER_TOKEN,
        'name': card_name, 
        'idList': list_id   
    }
    
    if description:
        params['desc'] = description  # Optional: Card description

    response = requests.post(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None 