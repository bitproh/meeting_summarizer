import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from tkinter.ttk import Progressbar
import subprocess
import sys
import os
import threading
import record_audio

# ---------------- PATHS & PYTHON ----------------

PYTHON = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Recorder process handle
recorder_process = None

# ---------------- BACKEND RUNNER (WITH PROGRESS) ----------------

def run_with_progress(script):
    process = subprocess.Popen(
        [PYTHON, os.path.join(BASE_DIR, script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        line = line.strip()

        # Loose keyword matching to work with the project's scripts
        if "Loading Whisper" in line or "Loading speech model" in line:
            status.set("Loading speech model…")
            progress.set(15)

        elif "Transcrib" in line:
            status.set("Transcribing audio…")
            progress.set(45)

        elif "Transcription completed" in line or "Transcript saved to" in line:
            status.set("Transcription completed.")
            progress.set(60)
            # load transcript into text area
            try:
                with open(os.path.join(BASE_DIR, "output", "transcript.txt"), "r", encoding="utf-8") as f:
                    text_area.delete("1.0", tk.END)
                    text_area.insert(tk.END, f.read())
            except FileNotFoundError:
                pass

        elif "Loading BART" in line or "Loading BART tokenizer" in line or "Loading summarization" in line:
            status.set("Loading summarization model…")
            progress.set(70)

        elif "Summariz" in line:
            status.set("Summarizing meeting…")
            progress.set(90)

        elif "Summarization completed" in line or "Bullet-point summary saved" in line:
            status.set("Summary ready.")
            progress.set(100)
            # load summary into text area
            try:
                with open(os.path.join(BASE_DIR, "output", "summary.txt"), "r", encoding="utf-8") as f:
                    text_area.delete("1.0", tk.END)
                    text_area.insert(tk.END, f.read())
            except FileNotFoundError:
                pass

        root.update_idletasks()

    process.wait()

# ---------------- RECORDING CONTROLS ----------------

def start_recording():
    # Start recorder using the importable API in a background thread
    status.set("Recording audio…")
    progress.set(5)

    def _start():
        try:
            record_audio.start_recording()
            process_btn.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Recorder Error", str(e))

    threading.Thread(target=_start, daemon=True).start()

def stop_recording():
    status.set("Stopping recording…")

    def _stop():
        try:
            out = record_audio.stop_recording()
            status.set("Recording completed.")
            progress.set(10)
            process_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Recording", "Audio recorded successfully.")
        except Exception as e:
            messagebox.showerror("Recorder Error", str(e))

    threading.Thread(target=_stop, daemon=True).start()

# ---------------- PROCESS MEETING ----------------

def process_meeting():
    def task():
        progress.set(10)
        status.set("Processing meeting…")

        try:
            run_with_progress("main.py")
            messagebox.showinfo("Done", "Meeting processed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=task).start()

# ---------------- DISPLAY & SAVE ----------------

def show_summary():
    try:
        with open(os.path.join(BASE_DIR, "output", "summary.txt"), "r", encoding="utf-8") as f:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, f.read())
        status.set("Summary loaded.")
    except FileNotFoundError:
        messagebox.showerror("Error", "No summary found. Please process first.")


def show_transcript():
    try:
        with open(os.path.join(BASE_DIR, "output", "transcript.txt"), "r", encoding="utf-8") as f:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, f.read())
        status.set("Transcript loaded.")
    except FileNotFoundError:
        messagebox.showerror("Error", "No transcription found. Please process first.")

def save_transcript():
    src = os.path.join(BASE_DIR, "output", "transcript.txt")
    if not os.path.exists(src):
        messagebox.showerror("Error", "No transcription found.")
        return

    dst = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )

    if dst:
        with open(src, "r", encoding="utf-8") as f_src, open(dst, "w", encoding="utf-8") as f_dst:
            f_dst.write(f_src.read())
        messagebox.showinfo("Saved", "Transcription saved.")

def save_summary():
    src = os.path.join(BASE_DIR, "output", "summary.txt")
    if not os.path.exists(src):
        messagebox.showerror("Error", "No summary found.")
        return

    dst = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )

    if dst:
        with open(src, "r", encoding="utf-8") as f_src, open(dst, "w", encoding="utf-8") as f_dst:
            f_dst.write(f_src.read())
        messagebox.showinfo("Saved", "Summary saved.")

# ---------------- UI ----------------

root = tk.Tk()
root.title("Offline Meeting Summarizer")
root.geometry("900x650")

tk.Label(
    root,
    text="Offline Meeting Summarizer",
    font=("Arial", 18, "bold")
).pack(pady=10)

# Recording buttons
tk.Button(root, text="🎙 Start Recording", width=45, command=start_recording).pack(pady=5)
tk.Button(root, text="⏹ Stop Recording", width=45, command=stop_recording).pack(pady=5)

# Process button (disabled until recording stops)
process_btn = tk.Button(
    root, text="🧠 Process Meeting",
    width=45, state=tk.DISABLED,
    command=process_meeting
)
process_btn.pack(pady=10)

# Progress bar
progress = tk.IntVar()
Progressbar(root, length=750, variable=progress, maximum=100).pack(pady=10)

# Status
status = tk.StringVar(value="Ready.")
tk.Label(root, textvariable=status).pack(pady=5)

# Output text area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=16)
text_area.pack(expand=True, fill="both", padx=10, pady=10)

# Bottom buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)


tk.Button(btn_frame, text="📄 Show Transcript", width=20, command=show_transcript).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="📄 Show Summary", width=20, command=show_summary).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="💾 Save Transcription (.txt)", width=20, command=save_transcript).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="💾 Save Summary (.txt)", width=20, command=save_summary).grid(row=0, column=3, padx=5)

root.mainloop()
