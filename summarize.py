import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm

# ---------------- CONFIG ----------------
INPUT_FILE = "output/transcript.txt"
OUTPUT_FILE = "output/summary.txt"
MODEL_NAME = "sshleifer/distilbart-cnn-12-6"
MAX_INPUT_TOKENS = 1024
# ----------------------------------------

def chunk_text(text, max_words=350):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i:i + max_words])

def main():
    os.makedirs("output", exist_ok=True)

    print("Loading BART tokenizer and model (CPU mode)...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    model.eval()  # inference mode

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = list(chunk_text(text))

    print("\nSummarizing transcript...\n")

    summaries = []

    progress_bar = tqdm(
        total=len(chunks),
        desc="Summarization progress",
        unit="chunk",
        ncols=80
    )

    for chunk in chunks:
        # 🔹 Prompt conditioning for bullet points
        prompt = (
            "Summarize the following meeting discussion into clear bullet points:\n\n"
            + chunk
        )

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_INPUT_TOKENS
        )

        with torch.no_grad():
            summary_ids = model.generate(
                inputs["input_ids"],
                max_length=150,
                min_length=60,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )

        summary_text = tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )

        summaries.append(summary_text)
        progress_bar.update(1)

    progress_bar.close()

    # 🔹 Clean formatting into bullets
    final_summary = []
    for s in summaries:
        lines = s.replace("•", "\n- ").replace("-", "\n- ").split("\n")
        for line in lines:
            line = line.strip()
            if line:
                if not line.startswith("-"):
                    line = "- " + line
                final_summary.append(line)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_summary))

    print("\nSummarization completed successfully.")
    print(f"Bullet-point summary saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
