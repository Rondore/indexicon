#!/usr/bin/env python3

import util
import settings
from logs import log

class FileLogger(log.Logger):
    def __init__(self, logfile: str) -> None:
        if logfile == 'scrape':
            logfile = util.get_install_path() + settings.scrape_log
        self.logfile = logfile
        self.output = open(logfile, 'w+')

    def log(self, message: str, line_ending='\n') ->  None:
        self.output.write(message + line_ending)