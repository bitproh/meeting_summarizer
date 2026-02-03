import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
import time

SAMPLE_RATE = 16000
CHANNELS = 1
DURATION_MINUTES = 5   # CHANGE THIS (e.g., 10, 30)

OUTPUT_FILE = "audio/meeting.wav"

def main():
    os.makedirs("audio", exist_ok=True)

    duration_seconds = DURATION_MINUTES * 60
    print(f"Recording for {DURATION_MINUTES} minutes...")

    recording = sd.rec(
        int(duration_seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32"
    )

    sd.wait()

    write(OUTPUT_FILE, SAMPLE_RATE, recording)
    print("Recording saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
