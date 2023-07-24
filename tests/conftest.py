import os
import pytest
import sqlite3


query_create_empty_db = '''
    CREATE TABLE BOOK_INFO (
        id      TEXT PRIMARY KEY
                    NOT NULL,
        asin    TEXT,
        guid    TEXT,
        lang    TEXT,
        title   TEXT,
        authors TEXT
    );
    CREATE TABLE DICT_INFO (
        id      TEXT PRIMARY KEY
                    NOT NULL,
        asin    TEXT,
        langin  TEXT,
        langout TEXT
    );
    CREATE TABLE LOOKUPS (
        id        TEXT    PRIMARY KEY
                        NOT NULL,
        word_key  TEXT,
        book_key  TEXT,
        dict_key  TEXT,
        pos       TEXT,
        usage     TEXT,
        timestamp INTEGER DEFAULT 0
    );
    CREATE TABLE METADATA (
        id        TEXT    PRIMARY KEY
                        NOT NULL,
        dsname    TEXT,
        sscnt     INTEGER,
        profileid TEXT
    );
    CREATE TABLE VERSION (
        id     TEXT    PRIMARY KEY
                    NOT NULL,
        dsname TEXT,
        value  INTEGER
    );
    CREATE TABLE WORDS (
        id        TEXT    PRIMARY KEY
                        NOT NULL,
        word      TEXT,
        stem      TEXT,
        lang      TEXT,
        category  INTEGER DEFAULT 0,
        timestamp INTEGER DEFAULT 0,
        profileid TEXT
    );
'''


@pytest.fixture(scope='session')
def example_db():
    '''
    Create a copy of example database in memory.
    '''
    db_file = 'tests/resources/vocab.test.db'
    if not os.path.exists(db_file):
        raise FileNotFoundError(f"The database file '{db_file}' does not exist.")
    src = sqlite3.connect(db_file)
    dst = sqlite3.connect(':memory:')
    src.backup(dst)
    src.close()

    yield dst

    dst.close()


@pytest.fixture(scope='function')
def empty_db():
    '''
    Create an empty database.
    '''
    # Create an empty in-memory database
    con = sqlite3.connect(':memory:')
    con.executescript(query_create_empty_db)

    yield con

    con.close()
