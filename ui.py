import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import sys
import os
import threading

# Always use the same Python that launched this script
PYTHON = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name):
    script_path = os.path.join(BASE_DIR, script_name)
    subprocess.run([PYTHON, script_path], check=True)

# ---------------- BUTTON ACTIONS ----------------

def record_meeting():
    def task():
        status.set("Recording meeting audio...")
        try:
            run_script("record_audio.py")
            status.set("Recording completed.")
            messagebox.showinfo("Recording", "Meeting audio recorded successfully.")
        except Exception as e:
            status.set("Recording failed.")
            messagebox.showerror("Error", str(e))

    threading.Thread(target=task).start()


def process_meeting():
    def task():
        status.set("Processing meeting (this may take time)...")
        try:
            run_script("main.py")
            status.set("Processing completed.")
            messagebox.showinfo("Done", "Meeting summarized successfully.")
        except Exception as e:
            status.set("Processing failed.")
            messagebox.showerror("Error", str(e))

    # Run heavy task in background thread (keeps UI responsive)
    threading.Thread(target=task).start()

def show_summary():
    try:
        with open(os.path.join(BASE_DIR, "output", "summary.txt"), "r", encoding="utf-8") as f:
            summary_text.delete("1.0", tk.END)
            summary_text.insert(tk.END, f.read())
        status.set("Summary loaded.")
    except FileNotFoundError:
        messagebox.showerror("Error", "No summary found. Please process a meeting first.")

# ---------------- UI SETUP ----------------

root = tk.Tk()
root.title("Offline Meeting Summarizer")
root.geometry("800x550")

# Title
title = tk.Label(root, text="Offline Meeting Summarizer", font=("Arial", 16, "bold"))
title.pack(pady=10)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="🎙 Record Meeting", width=25, command=record_meeting).pack(pady=5)
tk.Button(btn_frame, text="🧠 Process Meeting", width=25, command=process_meeting).pack(pady=5)
tk.Button(btn_frame, text="📄 Show Summary", width=25, command=show_summary).pack(pady=5)

# Summary display
summary_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
summary_text.pack(expand=True, fill="both", padx=10, pady=10)

# Status bar
status = tk.StringVar()
status.set("Ready.")
status_bar = tk.Label(root, textvariable=status, anchor="w", relief=tk.SUNKEN)
status_bar.pack(fill="x")

root.mainloop()

