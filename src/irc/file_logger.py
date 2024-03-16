import logging
import os

class FileLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s [%(levelname)s] %(message)s',
                            handlers=[logging.FileHandler(log_file),
                                      logging.StreamHandler()])

    def log(self, level, message):
        if level.lower() == 'debug':
            logging.debug(message)
        elif level.lower() == 'info':
            logging.info(message)
        elif level.lower() == 'warning':
            logging.warning(message)
        elif level.lower() == 'error':
            logging.error(message)

    def debug(self, message):
        self.log('debug', message)

    def info(self, message):
        self.log('info', message)

    def warning(self, message):
        self.log('warning', message)

    def error(self, message):
        self.log('error', message)
