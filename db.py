import sqlite3
import pandas as pd


def get_book_info(db_con):
  query_books = 'SELECT id, title FROM book_info'
  books = pd.read_sql_query(query_books, db_con)
  return books

def get_vocabs(db_con, book_id):
  args = (book_id,)
  cur = db_con.cursor()
  book_title = cur.execute(f'SELECT title FROM book_info WHERE id=?', args)
  # print(f'\nShowing vocabs of "{book_title.fetchone()[0]}":')

  query_vocabs = '''SELECT
    words.stem, lookups.usage, book_info.title
    FROM lookups
    JOIN book_info
    ON lookups.book_key = book_info.id AND
		  lookups.book_key=?
    JOIN words
    ON lookups.word_key = words.id'''
  vocabs = pd.read_sql_query(query_vocabs, db_con, params=args)
  vocabs.insert(loc=1, column='image', value='')
  vocabs.insert(loc=1, column='collocation', value='')
  vocabs.insert(loc=1, column='definition', value='')
  vocabs.insert(loc=1, column='audio', value='')
  vocabs.insert(loc=1, column='ipa', value='')
  return vocabs

if __name__ == "__main__":
  con = sqlite3.connect("vocab.db")

  # get books
  books = get_book_info(con)

  # select a book
  book_id = books['id'].iloc[8]

  # get vocabs of the book
  vocabs = get_vocabs(con, book_id)
  print(vocabs.head())
  # pprint(vocabs.head().values.tolist())

  con.close()
