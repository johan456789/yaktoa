import argparse
import genanki
from pywsd.lesk import simple_lesk

from db import *
from anki import *
from ipa import get_ipa


def get_def(sent, ambiguous):
  lexname_map = {
    'noun': 'n. ',
    'verb': 'v. ',
    'adj': 'adj. ',
    'adv': 'adv. '
  }
  try:
    synset = simple_lesk(sent, ambiguous)
    definition = synset.definition()
    lexname = lexname_map[synset.lexname().split('.')[0]]
    ans = f'{lexname}{definition}'
  except:
    ans = ''
  return ans

def ask_for_title(books):
  titles = [f'{str(idx).ljust(4)}{title}' for idx,
            title in enumerate(books['title'])]
  for title in titles:
    print(title)
  book_idx = int(
      input('Here are your books, which do you want to use (type number):'))
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
  print('Getting definitions...')
  vocabs['definition'] = vocabs[['stem', 'usage']].apply(
    lambda x: get_def(x['usage'], x['stem']), axis=1)
  vocabs['usage'] = vocabs[['word', 'usage']].apply(
    lambda x: x['usage'].replace(
      x['word'], '<b><i>' + x['word'] + '</i></b>'), axis=1)
  del vocabs['word']  # remove word and keep stem field only

  # get IPA
  if not args['no_ipa']:
    print('Getting IPA...')
    vocabs['ipa'] = vocabs['stem'].apply(lambda x: get_ipa(x))

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
  args = vars(ap.parse_args())

  con = sqlite3.connect(args['input'])
  main(con, args)
  con.close()
