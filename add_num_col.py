# checks the txts against the Sentence col to make a ordered Number col

import pandas as pd
from pathlib import Path
import re

def normalize(text: str) -> str:
    """
    Normalize text by:
      - Lowercasing
      - Removing all punctuation and non-letters
      - Converting multiple spaces to one
      - Trimming edges
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)  # Keep only letters and spaces
    text = re.sub(r"\s+", " ", text)       # Collapse multiple spaces
    return text.strip()

TEXT_DIR = Path("private/text")

df = pd.read_excel("FutureTokens102025.xlsx")

# Make sure columns exist
if "Number" not in df.columns:
    df["Number"] = None

results = []  # we'll collect all ordered groups

for speaker, group in df.groupby("Speaker_ID"):
    if not isinstance(speaker, str) or not speaker.startswith("CART"):
        continue

    speaker_code = speaker[4:6]  # e.g. "19"
    matching_files = list(TEXT_DIR.glob(f"{speaker_code}*"))

    if not matching_files:
        print(f"No text file found for {speaker}")
        continue

    text_file = matching_files[0]
    text_content = text_file.read_text(encoding="utf-8")

    normalized_text = normalize(text_content)

    ordered_group = group.copy()
    ordered_group["orig_index"] = group.index
    indices = []  # reset indices for each speaker

    for sentence in ordered_group["Sentence"]:
        norm_sentence = normalize(sentence)
        match = re.search(re.escape(norm_sentence), normalized_text)
        pos = match.start() if match else float("inf")
        indices.append(pos)

    ordered_group["IndexInText"] = indices

    # Sort within this speaker by appearance index
    ordered_group = ordered_group.sort_values("IndexInText").reset_index(drop=True)

    # Create Number like "CART19_1", "CART19_2", etc.
    ordered_group["Number"] = [f"{speaker}_{i+1}" for i in range(len(ordered_group))]

    results.append(ordered_group)

# Combine all processed speakers
if results:
    combined = pd.concat(results, ignore_index=True)

    # Write back Numbers to the original dataframe
    df.loc[combined["orig_index"], "Number"] = combined["Number"]

# Sort final df by speaker and number
df = df.sort_values(["Speaker_ID", "Number"], na_position="last").reset_index(drop=True)

output_file = "FutureTokens102625.xlsx"
df.to_excel(output_file, index=False)
print(f"Saved updated file to {output_file}")
