'''
Logger: the PyMT logger

Fifferents level are available :
    - debug
    - info
    - warning
    - error
    - critical

Examples of usage ::

    from pymt.logger import pymt_logger
    pymt_logger.notice('This is a notice')
    pymt_logger.debug('This is a notice')

    try:
        raise Exception('bleh')
    except Exception, e
        pymt_logger.exception(e)

'''

import logging
import os
import sys

__all__ = ('pymt_logger', 'LOG_LEVELS', 'COLORS', 'pymt_logger_history')

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': CYAN,
    'CRITICAL': RED,
    'ERROR': RED
}

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

use_color = True
if os.name == 'nt':
    use_color = False

class HistoryHandler(logging.Handler):
    history = []
    def emit(self, message):
        HistoryHandler.history = [message] + HistoryHandler.history[:100]

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        try:
            msg = record.msg.split(':', 1)
            if len(msg) == 2:
                record.msg = '[%-8s]%s' % (msg[0], msg[1])
        except:
            pass
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

class ColoredLogger(logging.Logger):
    FORMAT = '[%(levelname)-18s] %(message)s'
    COLOR_FORMAT = formatter_message(FORMAT, use_color)

    def __init__(self, name):
        global use_color
        logging.Logger.__init__(self, name, logging.DEBUG)
        color_formatter = ColoredFormatter(self.COLOR_FORMAT, use_color=use_color)
        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        # Use the custom handler instead of streaming one.
        if hasattr(sys, '_pymt_logging_handler'):
            self.addHandler(sys._pymt_logging_handler)
        else:
            self.addHandler(console)
        self.addHandler(HistoryHandler())
        return

logging.setLoggerClass(ColoredLogger)
pymt_logger = logging.getLogger('PyMT')
pymt_logger_history = HistoryHandler

