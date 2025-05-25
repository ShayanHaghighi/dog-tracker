import logging
import datetime
from .constants import LOG_PATH

LOG_LEVEL = logging.INFO

def logger_file_name():
    formatted_date = datetime.datetime.now().strftime('%Y%m%d')
    return f'{LOG_PATH}/{formatted_date}.log'

def Logger(file_name:str):
    file = logger_file_name()
    
    open(file, 'a').close()

    formatter = logging.Formatter('%(levelname)s|%(asctime)s|%(name)s|%(message)s',datefmt='%Y/%m/%d-%H:%M:%S')
    
    file_handler = logging.FileHandler(file)    
    file_handler.setFormatter(formatter)
    if '.' in file_name:
        logger = logging.getLogger(file_name[file_name.index('.')+1:])
    else:
        logger = logging.getLogger(file_name)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(file_handler)
        
    return logger

# logger = Logger(__name__)

# logger.info('hello')

