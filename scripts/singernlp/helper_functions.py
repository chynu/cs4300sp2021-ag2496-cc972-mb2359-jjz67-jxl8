import json

import pandas as pd
import sqlite3

import re
import unidecode as ud


def clean_str(input_artist, cap_code=0, opt_replacements=None):
    """
    Takes in string, returns a unicode-friendly and stripped version of the string.
    """
    return_artist_str = input_artist

    # === REGEX REPLACE ===
    repl_tuples = [(r'(^\s+)|(\s+$)', ''),  # whitespace at beg/end of string
                   (r'\s+', ' '),  # Remove double spaces
                   (r'[\n|\r|\t|\0]+', ' ')
                   ]
    if opt_replacements is not None:
        repl_tuples.extend(opt_replacements)
    for ptn, repl_str in repl_tuples:
        return_artist_str = re.sub(ptn, repl_str, return_artist_str)

    # === UNICODE HANDLING ===
    return_artist_str = ud.unidecode(return_artist_str)

    if cap_code == -1:
        return_artist_str = return_artist_str.lower()
    elif cap_code == 1:
        return_artist_str = return_artist_str.upper()

    return return_artist_str


def read_mard_json(input_filename):
    """
    Takes in file name of JSON, returns a list of dictionaries in which
    each element is a row with columns (as the keys).
    """
    loaded_data_ = []
    with open(input_filename, 'r') as file_:
        loaded_string_ = file_.read()
        loaded_data_ = [json.loads(s) for s in loaded_string_.split('\n') if s is not None and len(s) > 0]
        file_.close()
    return loaded_data_


def read_mard_json_as_df(input_filename):
    """
    Takes in file name of JSON, returns a list of dictionaries in which
    each element is a row with columns (as the keys).
    """
    loaded_data_ = []
    with open(input_filename, 'r') as file_:
        loaded_string_ = file_.read()
        loaded_data_ = [json.loads(s) for s in loaded_string_.split('\n') if s is not None and len(s) > 0]
        file_.close()
    return pd.DataFrame(loaded_data_)


def run_query_on_sqlite_db(input_query, input_filename):
    """

    Returns a Pandas DataFrame object containing the query results,
    given the user's query and the filename for the sqlite database.

    Input:
     - input_query: string representation of the SQL query to run on the sqlite db
     - input_filename: the file location of the sqlite database

    """
    conn_ = sqlite3.connect(input_filename)
    df_ = pd.read_sql_query(input_query, conn_)
    conn_.close()
    return df_
