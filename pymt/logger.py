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


By default, logger log also in a file, with the according configuration token ::

    [pymt]
    # will be stored in a "logs" directory in pymt home
    log_dir = logs
    # name of the log, according to time.strftime format
    # the %_ will be incremented from 0 to 10000 if the first
    # part of name already exist
    log_name = pymt_%y-%m-%d_%_.txt
    # activate or deactivate logs
    log_enable = 1

'''

import logging
import os
import sys

__all__ = ('pymt_logger', 'LOG_LEVELS', 'COLORS', 'pymt_logger_history',
           'pymt_logfile_activated')

pymt_logfile_activated = False

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

class FileHandler(logging.Handler):
    history = []
    filename = 'log.txt'
    fd = None

    def _configure(self):
        global pymt_logfile_activated
        import pymt, time
        log_dir = pymt.pymt_config.get('pymt', 'log_dir')
        log_name = pymt.pymt_config.get('pymt', 'log_name')

        _dir = pymt.pymt_home_dir
        if len(log_dir) and log_dir[0] == '/':
            _dir = log_dir
        else:
            _dir = os.path.join(_dir, log_dir)
            if not os.path.exists(_dir):
                os.mkdir(_dir)
        pattern = log_name.replace('%_', '@@NUMBER@@')
        pattern = os.path.join(_dir, time.strftime(pattern))
        n = 0
        while True:
            filename = pattern.replace('@@NUMBER@@', str(n))
            if not os.path.exists(filename):
                break
            n += 1
            if n > 10000: # prevent maybe flooding ?
                raise Exception('Too many logfile, remove them')

        FileHandler.filename = filename
        FileHandler.fd = open(filename, 'w')

        pymt.pymt_logger.info('Logger: Record log in %s' % filename)

    def _write_message(self, record):
        if FileHandler.fd in (None, False):
            return

        FileHandler.fd.write('[%-18s] %s\n' % (record.levelname, record.msg))
        FileHandler.fd.flush()

    def emit(self, message):
        if not pymt_logfile_activated:
            FileHandler.history += [message]
            return

        if FileHandler.fd is None:
            try:
                self._configure()
            except:
                # deactivate filehandler...
                FileHandler.fd = False
                pymt_logger.exception('Error while activating FileHandler logger')
                return
            for _message in FileHandler.history:
                self._write_message(_message)

        self._write_message(message)


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
        self.addHandler(FileHandler())
        return

logging.setLoggerClass(ColoredLogger)

#: PyMT default logger instance
pymt_logger = logging.getLogger('PyMT')

#: PyMT history handler
pymt_logger_history = HistoryHandler

