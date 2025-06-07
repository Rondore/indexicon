#!/usr/bin/env python3

import settings
from db.db_backend import DbBackend

_backend: (None | DbBackend) = None
        
def get_db() -> DbBackend:
    global _backend
    if _backend is not None:
        return _backend
    match settings.db_type:
        case 'mysql':
            from db import mysql
            return mysql.MySql()
        case 'maria' | 'mariadb':
            from db import mariadb
            return mariadb.Maria()
        case _:
            from db import sqlite
            _backend = sqlite.SqLite()
            return _backend