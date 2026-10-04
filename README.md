# SpanishFutureResearch

Code I'm using to research how Spanish speakers express the future: the morphological future (*hablaré*), the periphrastic future (*voy a hablar*), and the present with future meaning (*mañana hablo*). It pulls candidate future-time verb tokens out of sociolinguistic interview transcripts (currently the Medellín corpus) so they can be coded by hand and analyzed for variation.

Transcripts aren't public, so everything reads from and writes to a gitignored `private/` folder.

## Pipeline

You'll need [uv](https://docs.astral.sh/uv/getting-started/installation/), [LibreOffice](https://www.libreoffice.org/) for old `.doc` transcripts, and [TagAnt](https://www.laurenceanthony.net/software/tagant/). Run `uv sync` once, then:

1. Put the transcripts in `private/original/`.
2. `uv run to_txt.py` converts `.doc`/`.docx` to text in `private/txt/` and drops the header block above the `====` separator line.
3. `uv run clean_for_tagant.py` keeps only interviewee turns (tags `I`, `I.`, `B`), strips parentheticals and `<...>` annotations, flattens whitespace, and drops the first 350 words of each interview (the warm-up) into `private/clean_txt/`.
4. Tag `private/clean_txt/` with TagAnt's Spanish model using "word+pos_tag+lemma", and save the output to `private/tagged/`.
5. `uv run make_df.py` writes `private/future_data_MEDE_<date>.csv`/`.xlsx`, plus a `_nosimple` version without the present-tense candidates.
6. `uv run add_num_col.py` (optional) numbers each speaker's tokens in the order they appear in the transcript, so coded spreadsheets can be matched back to the text.

## How tokens are classified

Every VERB/AUX token (plus forms of *ir* and common auxiliaries) with a future or present ending is a candidate. Words containing endings that rule out a future reading (*-ndo*, *-ía*, *-ba*, clitics, ...) are skipped unless the ending belongs to the lemma. The rest get a `Future_marker`:

| Marker | Rule | Example |
|---|---|---|
| `morphological` | ends in a future ending (*-ré, -rás, -rá, -remos, -réis, -rán*) | *tendremos* |
| `possible periphrastic` | present of *ir* + *a* + verb | *voy a ver* |
| `possible simple` | present-tense form; needs manual coding for future meaning | *mañana salgo* |

Each row keeps five words of context on each side, both plain and POS-tagged, so the "possible" cases can be checked by hand.
