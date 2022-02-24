from __future__ import annotations

import configparser
import os

from .logging import get_logger

LOGGER = get_logger(__name__)


def get_config(project_path: str, error_logs: bool = False) -> configparser.ConfigParser:
    """
    Reads the project settings from the INI file, applies some defaults, and returns the config object.

    :param project_path: Project root path where the config file is located
    :param error_logs: Whether or not to log the config errors (default is False)
    :return: An object that contains configs
    """

    config = configparser.ConfigParser()

    # Set default sections
    config.add_section('environment')
    config.add_section('networking')
    config.add_section('logging')
    config.add_section('database')
    config.add_section('apps')
    config.add_section('middlewares')

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


def parse_list(string: str) -> tuple[str, ...]:
    """Parse the list from multi-line formatted string and convert it to a tuple type."""
    return tuple(i for i in string.split('\n') if i)
