'''Crawl definition, part of speech, phonetics, examples from oxfordlearnerdictionaries and find a longest sentence in each example'''
import requests
import re
from bs4 import BeautifulSoup
from collections import defaultdict
from tenacity import retry, stop_after_attempt, wait_fixed
def write_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def get_html_online(url):
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'
    response = requests.get(url, headers={'User-Agent': ua})
    return response.text

@retry(stop=stop_after_attempt(10), reraise=False, wait=wait_fixed(1))
def crawl_example(word):
    '''
    Crawl definition, part of speech, phonetics, examples from a data source and find a longest sentence in each example

    Args:
        word (str): The word to look up.

    Returns:
        tuple: A tuple containing the following information:
            - pos (str): The part of speech of the word.
            - definitions (list): A list of definitions for the word.
            - phonetics (list): A list of tuples containing the phonetic representation and audio URL for the word.
            - longest_sentences (list): A list of the longest sentences found in the examples for each definition.
            - extra_info (dict[list]): A dictionary containing additional information about each definition, should contain key: 'grammar' and 'labels'.
    Note: Length of each list should be identical to the number of definitions.
    '''
    url = ""
    
    

    return pos, definitions, phonetics, longest_sentences, extra_info

if __name__ == '__main__':
    pos, definitions, phonetics, longest_sentences, extra_info = crawl_example('abandon')
