
import numpy as np
import queue
import threading
import time
import soundcard as sc
from faster_whisper import WhisperModel
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.audio import Pipeline
import torch
from scipy.signal import resample
import logging
import warnings
import  os
# Load Faster Whisper Model (for transcription)
model = WhisperModel("small", device="cpu", compute_type="float32")

# Load Speaker Diarization Model
hug_token = os.getenv("HUGGINGFACE_TOKEN")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.0",
    use_auth_token=hug_token
)
pipeline.to(torch.device("cpu"))  # Use CPU

# Audio Settings
ORIGINAL_SAMPLE_RATE = 48000  # System audio default rate
TARGET_SAMPLE_RATE = 16000    # Whisper needs 16kHz
BLOCKSIZE = 16384 * 5         # Adjust block size for speed/latency tradeoff

# Audio Queue
audio_queue = queue.Queue()

# Get Default Speaker for Loopback Recording
speaker = sc.default_speaker()
mic = sc.get_microphone(id=str(speaker.name), include_loopback=True)

# Global timestamp tracking
start_time = time.time()

# Add logging configuration to suppress INFO messages
logging.getLogger("faster_whisper").setLevel(logging.WARNING)
logging.getLogger("speechbrain").setLevel(logging.WARNING)

# Suppress soundcard warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

def record_speaker():
    """Records system audio and queues it for transcription & diarization."""
    global start_time
    with mic.recorder(samplerate=ORIGINAL_SAMPLE_RATE) as spk_rec:
        print("🎤 Recording system audio...")

        while True:
            try:
                # Capture speaker output
                audio_chunk = spk_rec.record(numframes=BLOCKSIZE)

                # Convert stereo to mono
                audio_chunk = np.mean(audio_chunk, axis=1)

                # Resample to 16kHz if needed
                if ORIGINAL_SAMPLE_RATE != TARGET_SAMPLE_RATE:
                    audio_chunk = resample(audio_chunk, int(len(audio_chunk) * (TARGET_SAMPLE_RATE / ORIGINAL_SAMPLE_RATE)))

                # Compute timestamp
                current_time = time.time()
                elapsed_time = current_time - start_time  # Time elapsed since start

                # Add to processing queue with timestamp
                audio_queue.put((audio_chunk, elapsed_time))

            except KeyboardInterrupt:
                print("🛑 Stopped recording.")
                break

# Start Speaker Recording in a Thread
threading.Thread(target=record_speaker, daemon=True).start()

# Transcription & Diarization Loop
speaker_counter = 1  # Start from 1
speaker_mapping = {}

while True:
    try:
        # Fetch latest audio chunk
        audio_chunk, timestamp = audio_queue.get()

        # Convert audio chunk to float32 and proper tensor format
        audio_tensor = torch.tensor(audio_chunk, dtype=torch.float32).unsqueeze(0)

        # Transcribe using Faster Whisper
        segments, info = model.transcribe(audio_chunk, beam_size=5)

        # Skip if no speech detected
        segments = list(segments)  # Convert generator to list
        if not segments:
            continue

        # Perform speaker diarization with proper data type
        diarization_result = pipeline({
            "waveform": audio_tensor,
            "sample_rate": TARGET_SAMPLE_RATE
        })

        # Print transcriptions with timestamps and speakers
        for segment in segments:
            if not segment.text.strip():  # Skip empty transcriptions
                continue

            start_ts = timestamp + segment.start
            end_ts = timestamp + segment.end

            # Find the speaker associated with the segment
            speaker_label = f"Speaker {speaker_counter}"  # Default to next speaker number
            for turn, _, speaker in diarization_result.itertracks(yield_label=True):
                # Check if this turn overlaps with our segment
                if (turn.start <= segment.start and turn.end >= segment.end):
                    # If we haven't seen this speaker before, assign them a number
                    if speaker not in speaker_mapping:
                        speaker_mapping[speaker] = speaker_counter
                        speaker_counter += 1
                    speaker_label = f"Speaker {speaker_mapping[speaker]}"
                    break

            if segment.text.strip()!="You":  # Only print if there's actual text
                return f"[{start_ts:.2f}s - {end_ts:.2f}s] ({speaker_label}): {segment.text}"

    except KeyboardInterrupt:
        print("🛑 Stopped transcribing.")
        break