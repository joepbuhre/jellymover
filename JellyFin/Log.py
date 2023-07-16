import logging
import os
import sys

class ExitOnCritical(logging.Handler):
    def emit(self, record):
        
        if record.levelno in (logging.CRITICAL,):
            exit()

def get_logger(level: str = 'INFO'):

    log = logging.getLogger('JellyfinClient')
    
    log.setLevel(level=os.getenv('JWM_LOG_LEVEL', level).upper())
    
    # define handler and formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")

    # add formatter to handler
    handler.setFormatter(formatter)

    # add handler to logger
    log.addHandler(handler)

    log.addHandler(ExitOnCritical())  


    return log
    

