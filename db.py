import sqlite3
import pandas as pd


def get_book_info(db_con):
    query_books = 'SELECT id, title FROM book_info'
    books = pd.read_sql_query(query_books, db_con)
    return books


def get_vocabs(db_con, book_id):
    args = (book_id,)
    cur = db_con.cursor()
    book_title = cur.execute('SELECT title FROM book_info WHERE id=?', args).fetchone()
    if book_title is None:
        raise ValueError(f'No book found with ID: {book_id}')
    print(book_title[0])

    query_vocabs = '''SELECT
        words.stem, words.word, lookups.usage, book_info.title
        FROM lookups
        JOIN book_info
        ON lookups.book_key = book_info.id AND
            lookups.book_key=?
        JOIN words
        ON lookups.word_key = words.id'''
    vocabs = pd.read_sql_query(query_vocabs, db_con, params=args)
    vocabs.insert(loc=2, column='image', value='')
    vocabs.insert(loc=2, column='collocation', value='')
    vocabs.insert(loc=2, column='definition', value='')
    vocabs.insert(loc=2, column='audio', value='')
    vocabs.insert(loc=2, column='ipa', value='')
    return vocabs


if __name__ == "__main__":
    con = sqlite3.connect("vocab.db")

    books = get_book_info(con)
    book_id = books['id'].iloc[1]
    vocabs = get_vocabs(con, book_id)
    print(vocabs.head())

    con.close()
