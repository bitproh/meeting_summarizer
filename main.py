import subprocess
import sys
import os

def base_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE = base_path()
PYTHON = sys.executable  # ALWAYS use current interpreter

def run(script):
    subprocess.run(
        [PYTHON, os.path.join(BASE, script)],
        check=True
    )

print("=== OFFLINE MEETING SUMMARIZER ===")

print("[1/2] Transcribing audio...")
run("transcribe.py")

print("[2/2] Summarizing transcript...")
run("summarize.py")

print("DONE")
