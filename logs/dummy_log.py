#!/usr/bin/env python3

from logs import log

class DummyLogger(log.Logger):
    def log(self, message: str, line_ending='\n') ->  None:
        pass