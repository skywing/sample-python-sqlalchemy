from pathlib import Path
import logging
from typing import MutableMapping
import toml

logger = logging.getLogger(__name__)

class Configuration():
    def __init__(self):
        self.__config_file_path : str
        self.__config : MutableMapping

    def load(self, config_file_path: str = './config.toml'):
        logger.debug(f'loading config file: {config_file_path}')
        path = Path(config_file_path)
        if not path.exists():
            raise FileNotFoundError('File not found at {config_file_path}')
        self.__config_file_path = config_file_path
        self.__config = toml.load(self.__config_file_path)

    def get_config(self):
        logger.info('get_config called')
        logger.info(f'config: {self.__config}')
        return self.__config

    def get_config_file_path(self) -> str:
        logger.debug(f'get_config_file_path: {self.__config_file_path}')
        return self.__config_file_path
    
    def get_project(self):
        logger.info('get_project called')
        logger.debug(f'project settings: {self.__config["project"]}')
        return self.__config['project']
