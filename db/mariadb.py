#!/usr/bin/env python3

from mariadb.connectionpool import ConnectionPool
from mariadb.cursors import Cursor
import settings
from db.db_backend import DbBackend

def get_new_pool():
    """
    Cet a connected MySQL connection.
    """
    host = settings.db_host
    user = settings.db_user
    password = settings.db_password
    database = settings.db_db
    return ConnectionPool(host=host, user=user, password=password, database=database, pool_name="indexicon", pool_size=settings.db_pool)

pool = get_new_pool()

class Maria(DbBackend):
    def __init__(self):
        self.db = pool.get_connection()
        self.db.auto_reconnect = True

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

    def get_cursor(self) -> Cursor:
        return self.db.cursor(buffered=True)
    
    def close(self):
        self.db.close()