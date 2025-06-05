#!/usr/bin/env python3
from abc import ABC, abstractmethod

class Logger(ABC):
    def update_scrape_stamp(self, id: int) -> None:
        pass

    @abstractmethod
    def log(self, message: str, line_ending='\n') -> None:
        pass