import sqlite3
import pandas as pd
import pytest

from db import get_book_info, get_vocabs


class TestGetBookInfo:
    def test_returns_dataframe(self, example_db):
        con = example_db
        df = get_book_info(con)
        assert isinstance(df, pd.DataFrame)
        assert set(df.columns) == set(['id', 'title'])

    def test_insert_and_retrieve_book_info(self, empty_db):
        con = empty_db
        expected = pd.DataFrame({
            'id': ['1', '2', '3'],
            'title': ['Book 1', 'Book 2', 'Book 3'],
        })
        total_rows = len(expected)
        for i in range(total_rows):
            con.execute(f'INSERT INTO book_info (id, title) VALUES ("{expected.id[i]}", "{expected.title[i]}")')

        df = get_book_info(con)
        assert len(df) == total_rows
        assert df.equals(expected)

    def test_invalid_connection(self, empty_db):
        with pytest.raises(pd.errors.DatabaseError):
            con = sqlite3.connect('/tmp/invalid_db')  # creates an empty file if not exists
            get_book_info(con)


class TestGetVocabs:
    def test_invalid_book_id(self, empty_db):
        with pytest.raises(ValueError):
            get_vocabs(empty_db, '1')
