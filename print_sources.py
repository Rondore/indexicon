#!/t/www/private/venv/bin/python3

import sys
from db import database
from logs.log import Logger
from logs.terminal_log import TerminalLogger
from util import pretty_age

def print_sources(logger: Logger, only_enabled=True):
    """
    Get a list of all database sources, optionally filtered to just enabled sources
    """
    db = database.backend
    if only_enabled:
        logger.log("ID   COUNT   AGE   URL")
    else:
        logger.log("ID   ENALBED   COUNT   AGE   URL")
    def print_source(id: int, url: str, age: int, enabled: bool, count: int):
        if only_enabled:
            logger.log(str(id) + ' ' + str(count) + ' ' + pretty_age(age) + ' ' + url)
        else:
            logger.log(str(id) + ' ' + str(enabled) + ' ' + str(count) + ' ' + pretty_age(age) + ' ' + url)
    db.for_each_source_with_count(-1, print_source, only_enabled)

if __name__ == '__main__':
    enabled = len(sys.argv) > 1 and sys.argv[1].lower() == 'enabled'
    log = TerminalLogger()
    print_sources(log, enabled)
