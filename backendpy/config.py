from __future__ import annotations

import configparser
import os

from .logging import get_logger

LOGGER = get_logger(__name__)


def get_config(project_path: str, error_logs: bool = False) -> dict[str, dict[str, str | tuple[str]]]:
    """
    Reads the project settings from the INI file, applies some defaults, and returns the config as a dict object.

    :param project_path: Project root path where the config file is located
    :param error_logs: Whether or not to log the config errors (default is False)
    :return: A dict that contains configs
    """

    # Load from config file
    config_parser = configparser.ConfigParser()
    env_name = os.getenv('BACKENDPY_ENV', None)
    file_name = f'config.{env_name}.ini' if env_name is not None else 'config.ini'
    config_path = os.path.join(project_path, file_name)
    if os.path.exists(config_path):
        config_parser.read(config_path)
    elif error_logs:
        LOGGER.warning(f"Project {file_name} file does not exist")

    # Convert config to dict
    config = _to_dict(config_parser)

    # Add default sections if does not exists
    config.setdefault('environment', {})
    config.setdefault('networking', {})
    config.setdefault('logging', {})
    config.setdefault('database', {})
    config.setdefault('apps', {})
    config.setdefault('middlewares', {})

    # Add default configs if does not exists
    if type(config['apps'].get('active')) is not tuple:
        config['apps']['active'] = ()
    if type(config['middlewares'].get('active')) is not tuple:
        config['middlewares']['active'] = ()
    if type(config['networking'].get('allowed_hosts')) is not tuple:
        config['networking']['allowed_hosts'] = ()

    # Set environment configs
    config['environment']['project_path'] = str(project_path)
    config['environment']['project_name'] = os.path.basename(config['environment']['project_path'])

    # Check configs
    if config['environment'].get('media_path') and \
            not os.path.isdir(config['environment']['media_path']):
        raise LookupError("Project media path does not exist")

    return config


def _parse_list(string: str) -> tuple[str, ...]:
    """Parse the list from multi-line formatted string and convert it to a tuple type."""
    return tuple(i for i in string.split('\n') if i)


def _to_dict(cfg: configparser.ConfigParser) -> dict:
    """Convert config to dict"""
    r = dict()
    for section in cfg.sections():
        r[section] = dict()
        for k, v in cfg.items(section):
            r[section][k] = _parse_list(v) if '\n' in v else v
    return r
