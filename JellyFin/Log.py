import logging
import os

def get_logger():


    logging.basicConfig()

    log = logging.getLogger('JellyfinClient')
    
    log.setLevel(level=os.getenv('JWM_LOG_LEVEL', 'INFO').upper())
    
    return log
    