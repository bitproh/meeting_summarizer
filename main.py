import subprocess
import sys

PYTHON = sys.executable  # THIS IS THE FIX

print("=== OFFLINE MEETING SUMMARIZER ===")

print("\n[1/2] Transcribing audio...")
subprocess.run([PYTHON, "transcribe.py"], check=True)

print("\n[2/2] Summarizing transcript...")
subprocess.run([PYTHON, "summarize.py"], check=True)

print("\nDONE.")
print("Check the output folder.")
