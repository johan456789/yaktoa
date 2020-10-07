import genanki
from pywsd.lesk import simple_lesk

from db import *
from anki import *
from ipa import get_ipa

def get_def(sent, ambiguous):
  try:
    ans = simple_lesk(sent, ambiguous).definition()
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


def main(con):
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
  vocabs['usage'] = vocabs[['stem', 'usage']].apply(
    lambda x: x['usage'].replace(
      x['stem'], '<b><u>' + x['stem'] + '</u></b>'), axis=1)

  # get IPA
  print('Getting IPA...')
  vocabs['ipa'] = vocabs['stem'].apply(lambda x: get_ipa(x))
  print(vocabs.head())

  # export to apkg
  add_notes(my_deck, my_model, vocabs.values.tolist())
  save_apkg(my_deck)


if __name__ == "__main__":
  con = sqlite3.connect("vocab.db")
  main(con)
  con.close()
