import configparser
import os
from .logging import logging

LOGGER = logging.getLogger(__name__)


def get_config(project_path, error_logs=False):
    config = configparser.ConfigParser()

    # Set default sections
    config.add_section('environment')
    config.add_section('networking')
    config.add_section('logs')
    config.add_section('database')
    config.add_section('apps')
    config.add_section('middlewares')
    config.add_section('keys')

    # Set default configs
    config.set('apps', 'active', '')
    config.set('middlewares', 'active', '')

    # Load from config file
    env_name = os.getenv('BACKENDPY_ENV', None)
    file_name = f'config.{env_name}.ini' if env_name is not None else 'config.ini'
    config_path = os.path.join(project_path, file_name)
    if os.path.exists(config_path):
        config.read(config_path)
    elif error_logs:
        LOGGER.warning(f"Project {file_name} file does not exist")

    # Set environment configs
    config.set('environment', 'project_path', str(project_path))
    config.set('environment', 'project_name', os.path.basename(config['environment']['project_path']))

    # Check configs
    if config['environment'].get('media_path') and \
            not os.path.isdir(config['environment'].get('media_path')):
        raise LookupError("Project media path does not exist")

    return config


def parse_list(string):
    return tuple(i for i in string.split('\n') if i)
