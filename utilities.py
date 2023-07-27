import os
import sys
from contextlib import contextmanager
from typing import List
from nltk.corpus import wordnet as wn
from pywsd.lesk import simple_lesk
from pywsd.utils import lemmatize
from colorama import Style, Fore
import requests
from tqdm import tqdm
from dotenv import load_dotenv

from llm import wsd

tqdm.pandas()
load_dotenv()


@contextmanager
def silence_output(stdout=True, stderr=True):
    # Save the original stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        # Redirect stdout and stderr to a null device
        null_device = open(os.devnull, 'w')
        if stdout:
            sys.stdout = null_device
        if stderr:
            sys.stderr = null_device

        yield
    finally:
        # Restore stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def get_all_defs(word: str, dictionary='wordnet'):
    word = lemmatize(word)
    if dictionary == 'wordnet':
        word = word.replace(' ', '_')  # wn uses _ to combine compound words
        synsets = wn.synsets(word)
        return [get_wn_def(synset) for synset in synsets]
    elif dictionary == 'merriam-webster':
        try:
            pos_map = {
                'noun': 'n.',
                'verb': 'v.',
                'adjective': 'adj.',
                'adverb': 'adv.',
                'preposition': 'prep.',
                'pronoun': 'pron.',
                'conjunction': 'conj.',
                'interjection': 'interj.',
                'determiner': 'det.',
                'article': 'art.',
            }
            definitions = []
            entries = call_mw_api(word)
            for entry in entries:
                if type(entry) != dict or 'meta' not in entry:  # not an entry
                    continue
                if 'fl' not in entry or entry['fl'] not in pos_map:  # no pos tag
                    continue
                # if word.lower() not in entry['meta']['stems']:
                #     continue
                pos = pos_map[entry['fl']]
                for definition in entry['shortdef']:
                    definitions.append(f'{pos} {definition}')
                # TODO save usage info in "uns" and potentially example sentences in "vis"
        except Exception as e:
            print(f'In get_all_defs: {e}')
            definitions = []
        if not definitions:
            definitions = get_all_defs(word, dictionary='wordnet')  # fallback to wordnet
        return definitions
    else:
        raise ValueError(f'Unknown dictionary: {dictionary}')


def call_mw_api(word: str):
    '''
    Calls Merriam-Webster API and returns a list of entries

    :param word: word to look up
    :return: a list of entries

    Note:
    The API lemmatizes the word, so the returned entries may not contain the exact word.
    It's recommended to lemmatize the word before calling this function.
    # TODO: implement a rate limiter  # limit utilization of Hits per minute: 30/60 sec
    '''
    app_key = os.getenv('MERRIAM_WEBSTER_API_KEY')
    if app_key is None:
        raise ValueError('MERRIAM_WEBSTER_API_KEY is not set in .env')
    url = f'https://dictionaryapi.com/api/v3/references/learners/json/{word.lower()}?key={app_key}'
    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()
    return response.json()


def get_wn_def(synset):
    if synset is None:
        return ''
    lexname_map = {
        'noun': 'n.',
        'verb': 'v.',
        'adj': 'adj.',
        'adv': 'adv.',
    }
    definition = synset.definition()
    lexname = lexname_map[synset.lexname().split('.')[0]]
    return f'{lexname} {definition}'


def predict_def(sent: str, word: str, mode: str, definitions: List[str] = []) -> str:
    if mode == 'simple_lesk':
        try:
            word = word.replace(' ', '_')  # wn uses _ to combine compound words
            synset = simple_lesk(sent, word)
            return get_wn_def(synset)
        except Exception as e:
            print(f'In predict_def: {e}')
            return ''
    elif mode == 'chatgpt_wsd':
        if not definitions:
            return ''
        idx = wsd(sent, word, definitions, model='chatgpt') if len(definitions) > 1 else 0
        if idx == -1 or idx >= len(definitions):
            return ''  # TODO consider using chatgpt_generation as fallback
        return definitions[idx]
    elif mode == 'chatgpt_generation':
        raise NotImplementedError
    else:
        raise ValueError(f'Unknown mode: {mode}')


def get_def_manual(vocabs, mode='simple_lesk', dictionary='wordnet', report_incorrect=False):
    # TODO support different modes
    correct_count = incorrect_count = 0
    for vocab in vocabs.itertuples():
        definitions = get_all_defs(vocab.word, dictionary)
        if len(definitions) == 1:
            vocabs.loc[vocab.Index, 'definition'] = definitions[0]
        elif len(definitions) == 0:
            vocabs.loc[vocab.Index, 'definition'] = ''
        else:
            word_r = f'{Fore.RED}{vocab.word}{Style.RESET_ALL}'
            print(f'What does {word_r} mean in this context?\n"{vocab.usage.replace(vocab.word, word_r)}"')
            predicted_definition = predict_def(vocab.usage, vocab.stem, mode=mode, definitions=definitions)

            # print all definitions
            correct_idx = None
            for i, definition in enumerate(definitions):
                if definition == predicted_definition:
                    correct_idx = i
                    print(Fore.GREEN, end='')
                print(f'{str(i).ljust(4)}{definition}{Style.RESET_ALL}')

            user_input = input(f'({vocab.Index + 1}/{len(vocabs)}) Type number: ')
            idx = int(user_input) if user_input else -1  # TODO handle invalid input that can't be converted to int
            if user_input == '' or idx == correct_idx:  # choose predicted definition
                correct_count += 1
                vocabs.loc[vocab.Index, 'definition'] = predicted_definition
            else:
                incorrect_count += 1
                vocabs.loc[vocab.Index, 'definition'] = definitions[idx]
    if report_incorrect:
        total_wsd_count = incorrect_count + correct_count
        print(f'Of all {len(vocabs)} vocabs, {total_wsd_count} requires WSD.')
        if total_wsd_count > 0:
            accuracy = round(correct_count / total_wsd_count, 4) * 100
            print(f'WSD accuracy is {accuracy}% ({correct_count}/{total_wsd_count})')
    return vocabs


def get_def_auto(vocabs, mode='simple_lesk', dictionary='wordnet'):
    vocabs['definition'] = vocabs[['word', 'stem', 'usage']].progress_apply(
        lambda x: predict_def(x['usage'], x['stem'], mode=mode, definitions=get_all_defs(x['word'], dictionary)), axis=1
    )
    vocabs['usage'] = vocabs[['word', 'usage']].apply(
        lambda x: x['usage'].replace(x['word'], '<b><i>' + x['word'] + '</i></b>'), axis=1
    )
    return vocabs
