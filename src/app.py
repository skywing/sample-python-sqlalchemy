import ctypes
import logging
import logging.config
import toml
from util.configuration import Configuration

def main():
    logger.warning('This main function will pause this python \
        program by running in a paused loop.')
    while 1:
        logger.info('App is in pause mode. Ctrl+C to exit.')
        ctypes.CDLL(None).pause()

def log_debug():
    logger.debug('debugging message from main')

def log_info():
    logger.info('info message from main')

def log_warning():
    logger.warning('warning message from main')

def log_error():
    logger.error('error message from main')

def log_critical():
    logger.critical('critical message from main')

if __name__ == '__main__':
    log_config = toml.load('./log_config.toml')
    logging.config.dictConfig(dict(log_config))
    logger = logging.getLogger(__name__)

    log_debug()
    log_info()
    log_warning()
    log_error()
    log_critical()
    
    configuration = Configuration()
    configuration.load('./config.toml')
    configuration.get_config()
    configuration.get_config_file_path()
    project_config = configuration.get_project()
