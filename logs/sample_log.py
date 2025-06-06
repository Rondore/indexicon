#!/usr/bin/env python3

from logs import log

class SampleLogger(log.Logger):
    def __init__(self, size: int) -> None:
        self.size = size
        self.current_size = 0
        self.cursor = 0
        self.ring = [''] * size

    def log(self, message: str, line_ending='\n') ->  None:
        self.ring[self.cursor] = message
        self.cursor += 1
        if self.cursor >= self.size:
            self.cursor = 0;
        if self.current_size < self.size:
            self.current_size += 1

    def get_sample(self) -> str:
        if self.current_size == 0:
            return ''
        output = ''
        end = self.cursor - 1
        if end == -1:
            end = self.size - 1
        at = self.cursor - self.current_size
        if at < 0:
            at += self.size
        while True:
            output += self.ring[at] + '\n'
            if at == end:
                break
            at += 1
            if at >= self.size:
                at = 0
        return output
    
    def reset(self):
        self.current_size = 0
        self.cursor = 0