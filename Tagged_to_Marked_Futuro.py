# Creating the CSV file from the tagged transcipts

import os
import pandas as pd

future_endings = ["ré", "rás", "rá", "remos", "réis", "rán"]
ir_pres = ["voy", "vas", "va", "vamos", "vais", "van"]
pres_endings = ['o', 'as', 'a', 'amos', 'áis', 'an',
                   'e', 'es', 'e', 'emos', 'éis', 'en',
                   'imos', 'ís']
irr_pres_endings = ['oy', 'somos', 'sois', 'son', 'estás', 'está', 'están', 'hay']
all_pres_endings = pres_endings + irr_pres_endings
all_endings = future_endings + all_pres_endings + ir_pres

aux_pres_list = ['soy', 'eres', 'es' 'somos', 'sois', 'son', 
                 'estoy', 'estás', 'está', 'estamos', 'estáis', 'están', 
                 'he', 'has', 'ha', 'hay', 'hemos', 'habemos', 'habéis', 'han', 
                 'puedo', 'puedes', 'puede', 'podemos', 'podéis', 'pueden']

# list of endings that
redflag_list = ['ndo', 'ía', 'ba', 'ste', 
                'ra', 're', 'ri', 'ro', 'ru',
                'da', 'de', 'di', 'do', 'du',
                'te', 'lo', 'la', 'se', 'me', 'nos']

input_folder = "tagged"

# Create a list to store data frames
data_frames = []

for file in os.listdir(input_folder):
    speaker_ID = 'CART' + file[:2]
    file_path = os.path.join(input_folder, file)

    # Initialize a list to store row data
    rows = []

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

        # Split into sentences by period
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        for s in sentences:
            # keep only the first part before "_"
            words = [w.strip() for w in s.split(" ") if w.strip()]
            bare_words = [w.split("_")[0] for w in words if "_" in w]
            bare_s = " ".join(bare_words)

            for i, word in enumerate(words):
                parts = word.split("_")
                if len(parts) != 3:
                    continue

                bare_word, pos_tag, lemma = parts

                # must be verb/aux
                if not (pos_tag in ('VERB', 'AUX') or bare_word in aux_pres_list or bare_word in ir_pres):
                    continue

                # must have valid ending
                if not any(bare_word.endswith(form) for form in all_endings):
                    continue

                # skip redflag words
                if any(redflag in bare_word and redflag not in lemma for redflag in redflag_list) and lemma != 'ir':
                    continue

                fut_marker = 'possible simple'

                # Morphological future
                if any(bare_word.endswith(ending) for ending in future_endings):
                    fut_marker = 'morphological'

                # Possible periphrastic or simple future
                if bare_word in ir_pres and i + 2 < len(words):
                    next_word = words[i + 1]
                    next_next = words[i + 2]
                    if next_word.startswith("a_ADP") and (
                        next_next.split("_")[1] in ('VERB', 'AUX')
                    ):
                        fut_marker = 'periphrastic'

                # Add row only once, no removals
                row_data = {
                    'Speaker_ID': speaker_ID,
                    'Sentence': bare_s,
                    'POS_sentence': s,
                    'Verb': bare_word,
                    'POS_Verb': word,
                    'Future_marker': fut_marker
                }
                rows.append(row_data)

    # Create a DataFrame for the current file and append it to the list
    df = pd.DataFrame(rows)
    data_frames.append(df)
    print(f"Appended DataFrame for file: {file}")

# Concatenate all data frames in the list
df = pd.concat(data_frames, ignore_index=True)

# Save the DataFrame to a CSV file
output_filepath = 'private/FutureTokens92025.csv'
df.to_csv(output_filepath, index=False)
excel_filepath = output_filepath.replace('.csv', '.xlsx')
df.to_excel(excel_filepath, index=False)

# Save version without possible simple
df = df[df['Future_marker'] != 'possible simple']
output_filepath = 'private/FutureTokens92025_nosimple.csv'
df.to_csv(output_filepath, index=False)
excel_filepath = output_filepath.replace('.csv', '.xlsx')
df.to_excel(excel_filepath, index=False)