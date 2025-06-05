#!/usr/bin/env python3

import settings

def _get_db():
    match settings.db_type:
        case 'maria' | 'mariadb' | 'mysql':
            from db import maria
            return maria.Maria()
        case _:
            from db import sqlite
            return sqlite.SqLite()
        
backend = _get_db()