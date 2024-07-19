# GPTCloze

A set of helper scripts that efficiently generate Anki cards with LLM to help to memorize english words. One cloze card is made for each definition of a word.

The front of the card is an example sentence of a word and the back is the definition and phonetics of the word. LLM translates the definitions and the example sentence into Chinese and then marks the word in the example sentence.

The quality of generated cards depends largely on LLM. Mistranslation and mismarking are possible and expected.

## Prerequisites

- API key for OpenAI or other LLM service with OpenAI-compatible API
- Python 3.12
- Anki with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) installed

## Steps

1. Prepare a word list. (Example `data/dictionary.json`, Chinese translation is not necessary)
2. Prepare `crawl_example.py`  that should crawl definition, part of speech, phonetics, examples and some extra information from a specific data source.
3. Modify the API key in `openai_chat.py`. Modify base url if you use alternate LLM service.
4. Install dependencies: `pip install -r requirements.txt`.
5. Run `python make_cloze.py` to get a list of clozes at `data/cloze.json`.
6. Import `cloze_template.apkg` to import necessary Anki Card Template.
7. Run `make_anki_deck.py` to submit cards to Anki Deck specified by  `DECK_NAME` in `make_anki_deck.py`.

