import logging
import os

def get_logger():
    logging.basicConfig(level=logging.DEBUG)

    log = logging.getLogger('JellyfinClient')

    return log
    