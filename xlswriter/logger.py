import logging

class Logger(object):
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        if not len(self.logger.handlers):
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s]:%(name)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            # self.logger.setLevel(logging.INFO)