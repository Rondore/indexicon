from logs.log import Logger

class CompoundLogger(Logger):
    loggers: list[Logger]

    def __init__(self) ->  None:
        self.loggers = []

    def log(self, message: str, line_ending='\n') ->  None:
        for output in self.loggers:
            output.log(message, line_ending)

    def add_log(self, logger: Logger) ->  None:
        self.loggers.append(logger)