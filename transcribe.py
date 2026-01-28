import os
import soundfile as sf
from faster_whisper import WhisperModel
from tqdm import tqdm

# ---------------- CONFIG ----------------
AUDIO_FILE = "audio/meeting.wav"
OUTPUT_FILE = "output/transcript.txt"
MODEL_SIZE = "small"
# ----------------------------------------

def main():
    # Ensure output folder exists
    os.makedirs("output", exist_ok=True)

    # Load audio to calculate duration
    audio, samplerate = sf.read(AUDIO_FILE)
    audio_duration = len(audio) / samplerate  # seconds

    print("Loading Whisper model (CPU mode)...")
    model = WhisperModel(
        MODEL_SIZE,
        device="cpu",          # 🔴 FORCE CPU (fixes CUDA error)
        compute_type="int8"    # Optimized for CPU
    )

    print("Transcribing meeting audio...\n")

    segments, info = model.transcribe(AUDIO_FILE)

    progress_bar = tqdm(
        total=audio_duration,
        unit="sec",
        desc="Transcription progress",
        ncols=80
    )

    last_end = 0.0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for segment in segments:
            # Write text
            f.write(segment.text.strip() + " ")

            # Update progress bar using timestamps
            progress_bar.update(segment.end - last_end)
            last_end = segment.end

    progress_bar.close()

    print("\nTranscription completed successfully.")
    print(f"Transcript saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
