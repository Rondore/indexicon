#!/usr/bin/env python3

from mysql import connector
from mysql.connector.cursor import MySQLCursor
import settings
from db.db_backend import DbBackend

def get_new_connection():
    """
    Cet a connected MySQL connection.
    """
    host = settings.db_host
    user = settings.db_user
    password = settings.db_password
    database = settings.db_db
    return connector.connect(host=host, user=user, password=password, database=database, pool_name="indexicon", pool_size=settings.db_pool)

class MySql(DbBackend):
    def __init__(self):
        self.db = get_new_connection()

    def execute_and_close(self, query: str, values=()) -> None:
        cursor = self.get_cursor()
        cursor.execute(query, values)
        cursor.close()

    def execute_and_return(self, query: str, values=()):
        cursor = self.get_cursor()
        cursor.execute(query, values)
        return cursor
    
    def commit(self) -> None:
        self.db.commit()

    def stand_in_string(self) -> str:
        return '%s'

    def unix_time(self) -> str:
        return 'UNIX_TIMESTAMP()'

    def get_cursor(self) -> MySQLCursor:
        if not self.db.is_connected():
            self.db.reconnect()
        return self.db.cursor(buffered=True)
    
    def close(self):
        self.db.close()