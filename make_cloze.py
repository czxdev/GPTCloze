'''Make cloze test cards for specified word list with the help of LLM'''
'''position of word list: data/dictionary.json'''
import json
from crawl_example import crawl_example
from tqdm import tqdm
from openai_chat import run_conversation
import re
import time
from tenacity import retry, stop_after_attempt

log_file = f'data/log{time.time()}.txt'
log = open(log_file, 'w', encoding='utf-8')

pos_mapping = {'vt.': 'verb', 'vi.': 'verb','v.': 'verb', 'adj.': 'adjective',
               'adv.': 'adverb', 'n.': 'noun', 'prep.': 'preposition', 'conj.': 'conjunction'}

def logging(content:str):
    tqdm.write(content)
    log.write(content + '\n')
    log.flush()

def get_pos_set(def_items:list[dict]) -> set:
    pos_set = set()
    for item in def_items:
        pos = item['pos']
        if '/' in pos:
            # handle multiple part of speech split by '/'
            pos_queue = pos.split('/')
        else:
            pos_queue = [pos]
        for pos in pos_queue:
            if pos == '词组' or pos == '':
                # ignore the phrase
                continue
            if pos in pos_mapping:
                # map the part of speech to the standard part of speech
                pos_set.add(pos_mapping[pos])
            else:
                raise KeyError(f'fail to map part of speech {pos}')
    return pos_set

def load_dictionary(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        dictionary = json.load(f)
    return dictionary

def get_prompt(expression, definition, sentence):
    example_sentence = r'He {{manifested}} a pleasing personality on stage.'
    example_translation = r'他在舞台上{{展现出}}迷人的个性。'
    example_definition = r'显现出'
    double_bracket = r'{{}}'
    return f'''
You are helping an English learner to generate a memory card with an English sentence and its Chinese translation. You will be provided a target sentence, a target expression and the english definition of the target expression. You have to do the following things: 1. Repeat the target sentence with the target expression embraced in the sentecne with {double_bracket}. 2. Translate the target sentence into Chinese and embrace the Chinese translation of the target expression with {double_bracket} in the sentence translation. 3. Translate the target expression according to its english definition
Here is an example for your task:
Inputs:
Target sentence: He manifested a pleasing personality on stage.
Target expression: manifest
Definition: to show something clearly, especially a feeling, an attitude or a quality

Outputs:
Sentence: {example_sentence}
Sentence Translation: {example_translation}
Definition Translation: {example_definition}

Extra Demands: Never add any irrelated prompt to the aforementioned tasks. Never repeat the task descriptions in the response. Response of each task is prefixed with 'Sentence:', 'Sentence Translation:', and 'Definition Translation:'.

Input:
Target sentence: {sentence}
Target expression: {expression}
Definition: {definition}
'''

def make_card(word:str, pos:str, phonetics:str, extra_info:dict,
              definition:str, definition_translated:str, 
              cloze:str, cloze_translated:str) -> dict:
    '''make a cloze test card with the word, part of speech, definition and sentence'''
    card = {'word': word, 'pos': pos, 'phonetics': phonetics, 'extra_info': extra_info,
            'definition': definition, 'definition_translated': definition_translated,
            'cloze': cloze, 'cloze_translated': cloze_translated}
    return card

extract_pattern = re.compile(r'Sentence:(.*)\n.*Sentence Translation:(.*)\n.*Definition Translation:(.*)')
replace_pattern = re.compile(r'{{(.*)}}')
replace_pattern1 = re.compile(r'{{(?!c1::)(.*)}}')

class ExtractError(Exception):
    def __init__(self, message:str):
        self.message = message
    def __str__(self):
        return self.message

@retry(stop=stop_after_attempt(3), reraise=True)
def interact_with_openai_api(expression, definition, sentence) -> str:
    generated_prompt = get_prompt(expression, definition, sentence)
    response = run_conversation(generated_prompt).content
    extract_match = extract_pattern.search(response)
    if extract_match is None:
        raise ExtractError(f'fail to extract the cloze from the response: {response}')
    if len(extract_match.groups()) != 3:
        raise ExtractError(f'fail to extract the cloze from the response: {response}')
    cloze = extract_match.group(1).strip()
    cloze_translated = extract_match.group(2).strip()
    definition_translated = extract_match.group(3).strip()
    cloze = replace_pattern.sub(r'{{c1::\1}}', cloze) # replace the cloze with the anki cloze format
    cloze = replace_pattern1.sub(r'{{c1::\1}}', cloze)
    cloze = replace_pattern1.sub(r'{{c1::\1}}', cloze)
    cloze = replace_pattern1.sub(r'{{c1::\1}}', cloze)
    if r'{{c1::' not in cloze:
        # Just replace the first occurence of the word with the cloze format
        cloze = re.sub(f"({word})", r'{{c1::\1}}', cloze, flags=re.IGNORECASE)
    cloze_translated = cloze_translated.replace(r'{{', '<b>') # boldface the target expression with html tag
    cloze_translated = cloze_translated.replace(r'}}', '</b>')

    return cloze, cloze_translated, definition_translated

def make_cloze(word:str, pos_set:set[str], definition_list:dict = None) -> list[dict]:
    '''look up the expression with crawl_example.py for every part of speech in pos_list 
    and return the cloze test prompt for each definition in definition_list'''
    card_list = []
    for pos_index in range(len(pos_mapping)):
        # crawl the expression with the part of speech suffix
        if len(pos_set) == 0:
            break
        try:
            pos, definitions, phonetics, longest_sentences, extra_info = crawl_example(word + f"_{pos_index+1}")
        except Exception as e:
            logging(f'fail to crawl the example for {word}_{pos_index+1} with error: {str(e)}')
            continue
        if pos is None:
            break
        if pos not in pos_set or len(definitions) == 0:
            # no sense is available for the the specific part of speech
            continue
        if len(definitions) != len(longest_sentences):
            raise ValueError(f'the number of definitions and sentences differs for query {word}_{pos_index+1}')
        
        if len(extra_info.get('grammar')) != len(definitions):
            raise ValueError(f'the number of grammar information and definitions differs for query {word}_{pos_index+1}:\n{extra_info.get("grammar")}\n{definitions}')
        
        if len(extra_info.get('labels')) != len(definitions):
            raise ValueError(f'the number of labels information and definitions differs for query {word}_{pos_index+1}:\n{extra_info.get("labels")}\n{definitions}')
        
        pos_set.remove(pos)
        for def_i, definition in enumerate(definitions):
            sentence = longest_sentences[def_i]
            grammar = extra_info['grammar'][def_i]
            labels = extra_info['labels'][def_i]
            extra_info_for_def = {'grammar': grammar, 'labels': labels}
            if len(sentence.split()) < 5:
                logging(f'skip the example for {word} with less than 5 words: {sentence}')
                card = make_card(word, pos, phonetics, extra_info_for_def, definition, '', sentence, '')
                card_list.append(card)
            else:
                try:
                    cloze, cloze_translated, definition_translated = interact_with_openai_api(word, definition, sentence)
                except Exception as e:
                    logging(f'fail to get cloze for {word}_{pos_index+1} with error: {str(e)}')
                    card = make_card(word, pos, phonetics, extra_info_for_def, definition, '', sentence, '')
                    card_list.append(card)
                    continue
                card = make_card(word, pos, phonetics, extra_info_for_def, definition, definition_translated, cloze, cloze_translated)
                card_list.append(card)

    return card_list

def save_cards(card_list:list[dict], file_path:str):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(card_list, f, ensure_ascii=False)

if __name__ == '__main__':
    dictionary = load_dictionary('data/dictionary.json')
    word_count = len(dictionary)
    count = 0
    full_card_list = []
    STARTING_INDEX = 0
    STOPPING_INDEX = 100000
    for word, def_items in tqdm(dictionary.items()):
        if count < STARTING_INDEX: # skip some words
            count += 1
            continue
        pos_set = get_pos_set(def_items)
        logging(f'{word}: {pos_set}')
        full_card_list.extend(make_cloze(word, pos_set=pos_set, definition_list=def_items))
        count += 1
        if count % 100 == 0:
            #save_cards(full_card_list, f'data/cloze_{count}.json')
            #logging(f'save {STARTING_INDEX}-{count} cards')
            pass
        if count > STOPPING_INDEX: # limit the number of words to process
            break
    
    save_cards(full_card_list, 'data/cloze.json')
    

log.close()