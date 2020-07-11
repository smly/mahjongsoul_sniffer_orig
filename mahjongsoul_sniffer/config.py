#!/usr/bin/env python3

import pathlib
import typing
import yaml
from typing import Optional
import jsonschema


_config_schema = {
    'type': 'object',
    'required': ['logging'],
    'properties': {
        'logging': {
            'type': 'object',
            'required': ['log_file'],
            'properties': {
                'level': {
                    'enum': [
                        'DEBUG',
                        'INFO',
                        'WARNING',
                        'ERROR',
                        'CRITICAL',
                        None
                    ]
                },
                'log_file': {
                    'type': 'object',
                    'required': ['path'],
                    'properties': {
                        'path': {
                            'type': 'string'
                        },
                        'max_bytes': {
                            'oneOf': [
                                {
                                    'type': 'integer',
                                    'minimum': 0
                                },
                                {
                                    'const': None
                                }
                            ]
                        },
                        'backup_count': {
                            'oneOf': [
                                {
                                    'type': 'integer',
                                    'minimum': 0
                                },
                                {
                                    'const': None
                                }
                            ]
                        }
                    },
                    'additionalProperties': False
                }
            },
            'additionalProperties': False
        },
        'game_abstract': {
            'type': 'object',
            'required': [
                'storage'
            ],
            'properties': {
                'storage': {
                    'oneOf': [
                        {
                            'type': 'object',
                            'required': [
                                'type',
                                'bucket_name',
                                'key_prefix',
                            ],
                            'properties': {
                                'type': {
                                    'const': 'aws_s3'
                                },
                                'bucket_name': {
                                    'type': 'string'
                                },
                                'key_prefix': {
                                    'type': 'string'
                                }
                            },
                            'additionalProperties': False
                        },
                        {
                            'type': 'object',
                            'required': [
                                'type',
                                'prefix'
                            ],
                            'properties': {
                                'type': {
                                    'const': 'local'
                                },
                                'prefix': {
                                    'type': 'string'
                                }
                            },
                            'additionalProperties': False
                        }
                    ]
                }
            },
            'additionalProperties': False
        }
    },
    'additionalProperties': False
}


class Config(object):
    def __init__(self):
        config_file_path = pathlib.Path('config.yaml')
        if not config_file_path.exists():
            raise RuntimeError(
                f"Config file `{config_file_path}' does not exist.")
        if not config_file_path.is_file():
            raise RuntimeError(f"`{config_file_path}' is expected to be a"
                               " config file but not a file.")

        with open(config_file_path) as config_file:
            config = yaml.load(config_file, Loader=yaml.Loader)
        jsonschema.validate(instance=config, schema=_config_schema)

        self._config = config

    @property
    def logging_level(self) -> str:
        if 'level' in self._config['logging']:
            logging_level = self._config['logging']['level']
            if logging_level is None:
                logging_level = 'INFO'
        else:
            logging_level = 'INFO'
        return logging_level

    @property
    def log_file_path(self) -> pathlib.Path:
        return self._config['logging']['log_file']['path']

    @property
    def log_file_max_bytes(self) -> typing.Optional[int]:
        if 'max_bytes' in self._config['logging']['log_file']:
            log_file_max_bytes = \
                self._config['logging']['log_file']['max_bytes']
            if log_file_max_bytes == 0:
                log_file_max_bytes = None
        else:
            log_file_max_bytes = None
        return log_file_max_bytes

    @property
    def log_file_backup_count(self) -> typing.Optional[int]:
        if 'backup_count' in self._config['logging']['log_file']:
            log_file_backup_count = \
                self._config['logging']['log_file']['backup_count']
            if log_file_backup_count == 0:
                log_file_backup_count = None
        else:
            log_file_backup_count = None
        return log_file_backup_count

    @property
    def game_abstract_storage_type(self) -> str:
        return self._config['game_abstract']['storage']['type']

    @property
    def game_abstract_storage_prefix(self) -> Optional[str]:
        if self.game_abstract_storage_type != 'local':
            return None
        return self._config['game_abstract']['storage']['prefix']

    @property
    def game_abstract_storage_bucket_name(self) -> Optional[str]:
        if self.game_abstract_storage_type != 'aws_s3':
            return None
        return self._config['game_abstract']['storage']['bucket_name']

    @property
    def game_abstract_storage_key_prefix(self) -> Optional[str]:
        if self.game_abstract_storage_type != 'aws_s3':
            return None
        return self._config['game_abstract']['storage']['key_prefix']


config = Config()
