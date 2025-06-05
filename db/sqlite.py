#!/usr/bin/env python3

import settings
from db.db_backend import DbBackend
import sqlite3
from sqlite3 import Cursor

def get_new_connection():
    """
    Cet a connected SQLite connection.
    """
    host = settings.db_host
    return sqlite3.connect('data/' + host, check_same_thread=False)

class SqLite(DbBackend):
    def __init__(self):
        self.db = get_new_connection()
        cursor = self.db.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        name_list = cursor.fetchall()
        needs_init = len(name_list) < 4
        cursor.close()
        if needs_init:
            script = ''
            with open('setup.sql', 'r') as setup:
                for line in setup.readlines():
                    line = line.replace('AUTO_INCREMENT', '')
                    script += line + '\n'
            cursor = self.db.cursor()
            cursor.executescript(script)
            self.db.commit()
            cursor.close()

    def execute_and_close(self, query: str, values=()) -> None:
        cursor = self.db.cursor()
        cursor.execute(query, values)
        cursor.close()

    def execute_and_return(self, query: str, values=()):
        cursor = self.db.cursor()
        cursor.execute(query, values)
        return cursor
    
    def commit(self) -> None:
        self.db.commit()

    def stand_in_string(self) -> str:
        return '?'

    def unix_time(self) -> str:
        return 'unixepoch()'

    def get_cursor(self) -> Cursor:
        return self.db.cursor()