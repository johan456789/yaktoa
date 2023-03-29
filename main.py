import argparse
import sqlite3
import nltk
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('omw-1.4', quiet=True)

from db import get_book_info, get_vocabs
from anki import add_notes, save_apkg, my_model, my_deck
from ipa import get_ipa
from utilities import ask_for_book, get_def_manual, get_def_auto


def main(con, args):
    books = get_book_info(con)
    book_id, book_title = ask_for_book(books)

    print(f'Getting vocabulary of "{book_title}"...')
    vocabs = get_vocabs(con, book_id)

    if args['manual']:
        vocabs = get_def_manual(vocabs, report_incorrect=True)
    else:
        vocabs = get_def_auto(vocabs)
    del vocabs['word']  # remove word and keep stem column only

    if not args['no_ipa']:
        print('Getting IPA...')
        vocabs['ipa'] = vocabs['stem'].progress_apply(lambda x: get_ipa(x))

    if args['print']:
        print(vocabs.head())

    add_notes(my_deck, my_model, vocabs.values.tolist())
    save_apkg(my_deck, args['output'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Export Kindle vocabulary to Anki decks with definitions')
    ap.add_argument('-i', '--input', default='/Volumes/Kindle/system/vocabulary/vocab.db', help='Input filename')
    ap.add_argument('-o', '--output', default='output.apkg', help='Output filename')
    ap.add_argument('--no_ipa', action='store_true', help='Leave IPA field empty')
    ap.add_argument('-p', '--print', action='store_true', help='Print first 5 vocabularies')
    ap.add_argument('-m', '--manual', action='store_true', help='Manually select definition')
    args = vars(ap.parse_args())

    print(f'Input: {args["input"]}')
    print(f'Output: {args["output"]}\n')

    con = sqlite3.connect(args['input'])
    main(con, args)
    con.close()
