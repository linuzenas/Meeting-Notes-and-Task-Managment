import streamlit as st
from utils import (
    convert_audio_to_wav,
    transcribe_audio,
    summarize_text,
    extract_action_items,
    get_list_id_by_name,
    create_card_in_list
)
import requests

# Set page configuration
st.set_page_config(page_title="Meeting Notes and Task Management", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    body {
        background-color: #0d1b2a; /* Dark blue-black */
        color: #ffffff;
    }
    .stApp {
        background-color: #0d1b2a; /* Dark blue-black */
    }
    .stButton>button {
        background-color: #1b2631; /* Darker blue */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #3a506b; /* Lighter blue */
    }
    .stTextInput>div>input {
        background-color: #1b2631; /* Darker blue */
        color: white;
        border: 1px solid #3a506b; /* Lighter blue */
    }
    .stTextInput>div>label {
        color: #ffffff;
    }
    .stTextArea>div>textarea {
        background-color: #1b2631; /* Darker blue */
        color: white;
        border: 1px solid #3a506b; /* Lighter blue */
    }
    .stMarkdown {
        color: #ffffff;
    }
    .stHeader {
        font-size: 24px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Trello API configuration
API_KEY = 'your_api_key'  # Replace with your actual API key
USER_TOKEN = 'your_user_token'  # Replace with your actual user token
BOARD_ID = 'your_board_id'  # Replace with your actual board ID
BASE_URL = 'https://api.trello.com/1/'

# Streamlit interface
st.image("College logo.png", use_container_width=True)
st.title("Meeting Notes and Task Management")

# Create tabs
tab_upload, tab_transcription, tab_summary, tab_action_items = st.tabs(["Upload Audio", "Transcription", "Summary", "Action Items"])

with tab_upload:
    uploaded_file = st.file_uploader("Upload an Audio File", type=["wav", "mp3", "m4a"])

with tab_transcription:
    if uploaded_file:
        st.write("Processing uploaded audio file...")

        # Save uploaded file
        input_file_path = f"temp_audio.{uploaded_file.name.split('.')[-1]}"
        with open(input_file_path, "wb") as f:
            f.write(uploaded_file.read())

        # Convert audio to WAV
        wav_file_path = "converted_audio.wav"
        convert_audio_to_wav(input_file_path, wav_file_path)

        # Transcribe audio
        st.write("Transcribing audio...")
        audio_transcription = transcribe_audio(wav_file_path)

        # Display transcription with timestamps
        st.header("Transcription with Timestamps")
        for timestamp, segment in audio_transcription:
            st.write(f"[{timestamp}s]: {segment}")

        # Combine segments into full transcript
        full_transcript = " ".join([segment for _, segment in audio_transcription])

with tab_summary:
    if 'full_transcript' in locals():  # Check if full_transcript is defined
        st.write("Summarizing transcription...")
        summary = summarize_text(full_transcript)
        st.subheader("Meeting Summary")
        st.write(summary)
    else:
        st.warning("Please upload an audio file and transcribe it first.")

with tab_action_items:
    if 'full_transcript' in locals():  # Check if full_transcript is defined
        st.write("Extracting action items...")
        action_items = extract_action_items(full_transcript)
        st.subheader("Action Items")

        # Allow user to edit action items
        edited_action_items = []
        for item in action_items:
            edited_item = st.text_input("Edit Action Item:", value=item)
            edited_action_items.append(edited_item)

        st.write(edited_action_items)

        # Trello integration
        if st.button("Create Trello Cards for Action Items"):
            list_name = "To Do"  # Specify the list name as "To Do"
            list_id = get_list_id_by_name(BOARD_ID, list_name)
            
            if list_id:
                for task in edited_action_items:
                    create_card_in_list(list_id, task)
            else:
                st.warning("Could not find the specified list in Trello.")

        # Save the final notes
        if st.button("Save Meeting Notes"):
            with open("meeting_notes.txt", "w") as file:
                file.write(f"Meeting Transcript:\n{full_transcript}\n\nSummary:\n{summary}\n\nAction Items:\n{', '.join(edited_action_items)}")
            st.success("Meeting notes saved successfully.")
    else:
        st.warning("Please upload an audio file and transcribe it first.")

# Call this function to see the lists
def print_board_lists(board_id):
    url = f'{BASE_URL}boards/{board_id}/lists'
    params = {
        'key': API_KEY,
        'token': USER_TOKEN
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        lists = response.json()
        for lst in lists:
            print(f"List Name: {lst['name']}, List ID: {lst['id']}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

print_board_lists(BOARD_ID) 