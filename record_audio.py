import sounddevice as sd
from scipy.io.wavfile import write
import os

SAMPLE_RATE = 16000  # Whisper likes this
OUTPUT_FILE = "audio/meeting.wav"

os.makedirs("audio", exist_ok=True)

print("Press ENTER to start recording...")
input()

print("Recording... Press ENTER to stop.")
recording = []

def callback(indata, frames, time, status):
    recording.append(indata.copy())

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    
    callback=callback
):
    input()

audio = b"".join([chunk.tobytes() for chunk in recording])
audio_array = b"".join([chunk.tobytes() for chunk in recording])

import numpy as np
audio_np = np.concatenate(recording, axis=0)

write(OUTPUT_FILE, SAMPLE_RATE, audio_np)

print("Recording saved as:", OUTPUT_FILE)
