import argparse
import sqlite3
import genanki
import nltk_modules
from nltk.corpus import wordnet as wn
from colorama import Style, Fore
from tqdm import tqdm

from db import get_book_info, get_vocabs
from anki import add_notes, save_apkg, my_model, my_deck
from ipa import get_ipa


tqdm.pandas()

def get_def(synset):
    if synset is None:
        return ''
    lexname_map = {
        'noun': 'n. ',
        'verb': 'v. ',
        'adj': 'adj. ',
        'adv': 'adv. '
    }
    definition = synset.definition()
    lexname = lexname_map[synset.lexname().split('.')[0]]
    return f'{lexname}{definition}'

def predict(sent, ambiguous):
    try:
        return simple_lesk(sent, ambiguous)
    except:
        return None

def ask_for_title(books):
    titles = [f'{str(idx).ljust(4)}{title}' for idx, title in enumerate(books['title'])]
    for title in titles:
        print(title)
    book_idx = int(input('Here are your books, which do you want to use (type number):'))
    book_id = books['id'].iloc[book_idx]
    book_title = books['title'].iloc[book_idx]
    return book_id, book_title

def main(con, args):
    # get books
    books = get_book_info(con)

    # select a book
    book_id, book_title = ask_for_title(books)

    # get vocabs of the book
    vocabs = get_vocabs(con, book_id)

    # get definitions
    if args['manual']:
        incorrect_count = 0

        for vocab in vocabs.itertuples():
            synsets = wn.synsets(vocab.word)
            if len(synsets) == 1:
                vocabs.loc[vocab.Index, 'definition'] = get_def(synsets[0])
            elif len(synsets) == 0:
                vocabs.loc[vocab.Index, 'definition'] = ''
            else:
                word_r = f'{Fore.RED}{vocab.word}{Style.RESET_ALL}'
                print(f'What does {word_r} mean in this context?\n"{vocab.usage.replace(vocab.word, word_r)}"')
                synset_pred = predict(vocab.usage, vocab.stem)
                for i, synset in enumerate(synsets):
                    if synset == synset_pred:
                        correct_i = i
                        print(Fore.GREEN, end='')
                    print(f'{str(i).ljust(4)}{get_def(synset)}{Style.RESET_ALL}')

                user_input = input(f'({vocab.Index + 1}/{len(vocabs)}) Type number: ')
                if user_input == '':
                    vocabs.loc[vocab.Index, 'definition'] = get_def(synset_pred)
                else:
                    idx = int(user_input)
                    if idx != correct_i:
                        incorrect_count += 1
                    vocabs.loc[vocab.Index, 'definition'] = get_def(synsets[idx])
        print(f'WSD accuracy is {round(1 - incorrect_count / len(vocabs), 4) * 100}%')
    else:
        print('Getting definitions...')
        vocabs['definition'] = vocabs[['stem', 'usage']].progress_apply(
            lambda x: get_def(predict(x['usage'], x['stem'])), axis=1
        )
        vocabs['usage'] = vocabs[['word', 'usage']].apply(
            lambda x: x['usage'].replace(x['word'], '<b><i>' + x['word'] + '</i></b>'), axis=1
        )
    del vocabs['word']  # remove word and keep stem field only

    # get IPA
    if not args['no_ipa']:
        print('Getting IPA...')
        vocabs['ipa'] = vocabs['stem'].progress_apply(lambda x: get_ipa(x))

    # print result
    if args['print']:
        print(vocabs.head())

    # export to apkg
    add_notes(my_deck, my_model, vocabs.values.tolist())
    save_apkg(my_deck, args['output'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Export Kindle vocabulary to Anki decks with definitions')
    ap.add_argument('-i', '--input', default='vocab.db', help='Input filename')
    ap.add_argument('-o', '--output', default='output.apkg', help='Output filename')
    ap.add_argument('--no_ipa', action='store_true', help='Leave IPA field empty')
    ap.add_argument('-p', '--print', action='store_true', help='Print first 5 vocabularies')
    ap.add_argument('-m', '--manual', action='store_true', help='Manually select definition')
    args = vars(ap.parse_args())

    from pywsd.lesk import simple_lesk
    con = sqlite3.connect(args['input'])
    main(con, args)
    con.close()
