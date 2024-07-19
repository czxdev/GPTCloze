import json
import requests
import random

ANKI_CONNECT_URL = 'http://127.0.0.1:8765'

def ankiconnect_query(action:str, params:dict = None):
    query = {'action': action, 'version': 6, 'params': params or {}}
    response = requests.post(ANKI_CONNECT_URL, json=query)
    if response.json()['error']:
        raise Exception(response.json()['error'])
    return response.json()['result']

LINE_BREAK = '<br>\n'
SPACE = '&nbsp; '

def get_definition(card:dict):
    def span(class_:str, text:str):
        return f'<span class={class_}>{text}</span>'
    word = f"<b>{card['word']}</b>"
    extra_info = card['extra_info']['grammar'] + SPACE + card['extra_info']['labels']
    return LINE_BREAK + word + SPACE +  f"<i>{card['pos'] + SPACE*2 + extra_info}</i>" + LINE_BREAK +\
            span('endef',card['definition']) + LINE_BREAK + span('text_blue',card['definition_translated'])

def add_cards_to_deck(cards:list[dict], deck_name:str, card_model_name:str):
    def get_note(card:dict):
        note = {
            'deckName': deck_name,
            'modelName': card_model_name,
            'fields': {
                '挖空的例句': card['cloze'] + LINE_BREAK + card['cloze_translated'],
                '音标': '英' + card['phonetics'][0][0] + f'{SPACE}美' + card['phonetics'][1][0],
                '发音': f"[sound:{card['phonetics'][0][1]}]{SPACE}[sound:{card['phonetics'][1][1]}]",
                '释义': get_definition(card),
                '笔记': ''
            },
            'options': {
                'allowDuplicate': False
            }
        }
        return note
    note_list = [get_note(card) for card in cards]
    ankiconnect_query('addNotes', {'notes': note_list})

if __name__ == '__main__':
    DECK_NAME = 'Cloze Cards'
    if DECK_NAME not in ankiconnect_query('deckNames'):
        ankiconnect_query('createDeck', {'deck': DECK_NAME})
    ANKI_MODEL = '例句填空带释义发音'
    if ANKI_MODEL not in ankiconnect_query('modelNames'):
        raise Exception('Anki model not found, please import the model first')
    
    # try to get note
    #notes = ankiconnect_query('findNotes', {'query': f'deck:"Extensive Reading"'})
    #print(ankiconnect_query('notesInfo', {'notes': notes}))
    with open('./data/cloze.json', 'r', encoding='utf-8') as f:
        card_list = json.load(f)
    
    card_dict = {card['word'] + card['definition']: card for card in card_list}

    count = 0
    note_list = []
    BATCH_SIZE = 50
    # shuffle card list
    random.shuffle(card_list)
    # add cards to deck in batches
    for i in range(0, len(card_list), BATCH_SIZE):
        try:
            add_cards_to_deck(card_list[i:i+BATCH_SIZE], DECK_NAME, ANKI_MODEL)
        except Exception as e:
            print(f'Fail to add cards with error: {str(e)}')


    