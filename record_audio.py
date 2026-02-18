import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os
import sys
import signal

SAMPLE_RATE = 16000
CHANNELS = 1
OUTPUT_FILE = "audio/meeting.wav"


# Internal state used when controlling recorder from other modules (e.g. the UI)
_recording = []
_stream = None
_running = False


def _callback(indata, frames, time, status):
    global _recording
    if _running:
        _recording.append(indata.copy())


def start_recording():
    """Start recording in the current process. Returns True on success."""
    global _stream, _running, _recording

    if _running:
        print("[RECORDER] Already recording")
        return False

    os.makedirs("audio", exist_ok=True)
    _recording = []
    _running = True

    _stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=_callback
    )
    _stream.start()
    print("[RECORDER] Recording started")
    return True


def stop_recording():
    """Stop recording and write audio file. Returns path or None on failure."""
    global _stream, _running, _recording

    if not _running:
        print("[RECORDER] Not recording")
        return None

    _running = False
    try:
        if _stream is not None:
            _stream.stop()
            _stream.close()
    except Exception:
        pass

    if len(_recording) == 0:
        print("[RECORDER] No audio captured")
        return None

    audio = np.concatenate(_recording, axis=0)
    write(OUTPUT_FILE, SAMPLE_RATE, audio)
    print("[RECORDER] Recording stopped")
    print("[RECORDER] Audio saved to", OUTPUT_FILE)
    return OUTPUT_FILE


def main():
    # Backwards compatible CLI entrypoint that used signal handlers
    def stop_handler(signum, frame):
        stop_recording()

    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)

    start_recording()
    try:
        while True:
            sd.sleep(200)
    except KeyboardInterrupt:
        stop_recording()


if __name__ == "__main__":
    main()
