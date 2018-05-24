#!/usr/bin/env python
# -*-coding:utf-8 -*

import os
import yaml
import atexit
import click
import logging
import ovh

from configparser import ConfigParser
from ovh.exceptions import ResourceNotFoundError, BadParametersError
from scriptlock import Lock
from alkivi.logger import Logger

# Define the global logger
logger = Logger(min_log_level_to_mail=logging.CRITICAL,
                min_log_level_to_save=logging.DEBUG,
                min_log_level_to_print=logging.INFO,
                min_log_level_to_syslog=None,
                filename='/var/log/alkivi/backup-all-telephony.py.log',
                emails=['monitoring@alkivi.fr'])

# Optional lock file
LOCK = Lock()
atexit.register(LOCK.cleanup)

DEFAULT_PATH = '/home/backup-telephony'


def get_config():
    """Read configuration from script path and load it."""
    basedir = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(basedir, 'backup.conf')
    config = ConfigParser()
    if os.path.isfile(config_file):
        config.read(config_file)
    else:
        config['DEFAULT']['rootdir'] = DEFAULT_PATH

    return config


def get_default_dir():
    """Read rootdir from config."""
    config = get_config()
    return config['DEFAULT']['rootdir']


class BackupManager(object):
    """Class to handle all calls."""
    def __init__(self, client, group, rootdir, logger):
        self.client = client
        self.group = group
        self.rootdir = rootdir
        self.logger = logger
        self.status_to_skip = ['closed', 'expired']

    def backup(self):
        """Check status of group and backup if OK."""
        url = '/telephony/{0}'.format(self.group)
        data = self.client.get(url)
        if data['status'] in self.status_to_skip:
            logger.debug('service {0}, skipping'.format(data['status']))
            return
        self.backup_group()

    def backup_group(self):
        """Backup an entire group."""
        logger.info('backup started')

        # Backup abbreviatedNumber
        url = '/telephony/{0}/abbreviatedNumber'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='abbreviatedNumber={0}'.format(obj))
            self.backup_abbreviatedNumber(obj)
        logger.del_loop_logger()

        # Backup easyHunting
        url = '/telephony/{0}/easyHunting'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='easyHunting={0}'.format(obj))
            self.backup_easyHunting(obj)
        logger.del_loop_logger()

        # Backup easyPabx
        url = '/telephony/{0}/easyPabx'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='easyPabx={0}'.format(obj))
            self.backup_easyPabx(obj)
        logger.del_loop_logger()

        # Backup fax
        url = '/telephony/{0}/fax'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='fax={0}'.format(obj))
            self.backup_fax(obj)
        logger.del_loop_logger()

        # Backup line
        url = '/telephony/{0}/line'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='line={0}'.format(obj))
            self.backup_line(obj)
        logger.del_loop_logger()

        # Backup miniPabx
        url = '/telephony/{0}/miniPabx'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='miniPabx={0}'.format(obj))
            self.backup_miniPabx(obj)
        logger.del_loop_logger()

        # Backup number
        url = '/telephony/{0}/number'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='number={0}'.format(obj))
            self.backup_number(obj)
        logger.del_loop_logger()

        # Backup ovhPabx
        url = '/telephony/{0}/ovhPabx'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='ovhPabx={0}'.format(obj))
            self.backup_ovhPabx(obj)
        logger.del_loop_logger()

        # Backup phonebook
        url = '/telephony/{0}/phonebook'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='phonebook={0}'.format(obj))
            self.backup_phonebook(obj)
        logger.del_loop_logger()

        # Backup redirect
        url = '/telephony/{0}/redirect'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='redirect={0}'.format(obj))
            self.backup_redirect(obj)
        logger.del_loop_logger()

        # Backup scheduler
        url = '/telephony/{0}/scheduler'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='scheduler={0}'.format(obj))
            self.backup_scheduler(obj)
        logger.del_loop_logger()

        # Backup screen
        url = '/telephony/{0}/screen'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='screen={0}'.format(obj))
            self.backup_screen(obj)
        logger.del_loop_logger()

        # Backup service
        url = '/telephony/{0}/service'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='service={0}'.format(obj))
            self.backup_service(obj)
        logger.del_loop_logger()

        # Backup timeCondition
        url = '/telephony/{0}/timeCondition'.format(self.group)
        logger.new_loop_logger()
        for obj in self.client.get(url):
            logger.new_iteration(prefix='timeCondition={0}'.format(obj))
            self.backup_timeCondition(obj)
        logger.del_loop_logger()

        logger.info('backup ended')

    def _backup(self, data):
        """Helpers to parse save all the data correctly."""
        for k, v in data.items():
            if v['save']:
                self._save_data(k)

            logger.new_loop_logger()
            for children, children_data in v.get('children', {}).items():
                root = '{0}/{1}'.format(k, children)
                prefix = root[len(k)+1::]
                logger.new_iteration(prefix=prefix)
                description = {root: children_data}
                self._backup(description)
            logger.del_loop_logger()

            for clist, clist_data in v.get('lists', {}).items():
                base_url = '{0}/{1}'.format(k, clist)

                data = self._get_url(base_url)
                if not data:
                    continue

                logger.new_loop_logger()
                for obj in data:
                    root = '{0}/{1}'.format(base_url, obj)
                    prefix = root[len(k)+1::]
                    logger.new_iteration(prefix=prefix)
                    description = {root: clist_data}
                    self._backup(description)
                logger.del_loop_logger()

    def backup_abbreviatedNumber(self, number):
        """Backup abbreviatedNumber configuration."""
        logger.info('backup abbreviatedNumber')

        root_dir = '/telephony/{0}/abbreviatedNumber/{1}'.format(self.group, number)
        description = {root_dir: {'save': True}}
        self._backup(description)

    def backup_easyHunting(self, easyHunting):
        """Backup easyHunting configuration."""
        logger.info('backup easyHunting')

        root_dir = '/telephony/{0}/easyHunting/{1}'.format(self.group, easyHunting)
        description = {
            root_dir: {
                'save': True,
                'lists': {
                    'sound': {'save': True},
                },
                'children': {
                    'timeConditions': {
                        'save': True,
                        'lists': {
                            'conditions': {'save': True},
                        },
                    },
                    'screenListConditions': {
                        'save': True,
                        'lists': {
                            'conditions': {'save': True},
                        },
                    },
                    'hunting': {
                        'save': True,
                        'lists': {
                            'agent': {
                                'save': True,
                                'lists': {
                                    'queue': {'save': True},
                                },
                            },
                            'queue': {
                                'save': True,
                                'lists': {
                                    'agent': {'save': True},
                                },
                            },
                        },
                    },
                },
            },
        }
        self._backup(description)

    def backup_easyPabx(self, easyPabx):
        """Backup easyPabx configuration."""
        logger.info('backup easyPabx')

        root_dir = '/telephony/{0}/easyPabx/{1}'.format(self.group, easyPabx)
        description = {
            root_dir: {
                'save': True,
                'children': {
                    'hunting': {
                        'save': True,
                        'lists': {
                            'agent': {'save': True},
                        },
                        'children': {
                            'tones': {'save': True},
                        },
                    },
                },
            },
        }
        self._backup(description)
        exit(0)

    def backup_fax(self, fax):
        """Backup fax configuration."""
        logger.info('backup fax')

        root_dir = '/telephony/{0}/fax/{1}'.format(self.group, fax)
        description = {
            root_dir: {
                'save': True,
                'children': {
                    'settings': {'save': True},
                },
            },
        }
        self._backup(description)

    def backup_line(self, line):
        """Backup configuration of a line."""
        logger.info('backup line')

        # basic informations
        root_dir = '/telephony/{0}/line/{1}'.format(self.group, line)
        description = {
            root_dir: {
                'save': True,
                'lists': {
                    'abbreviatedNumber': {'save': True},
                },
                'children': {
                    'options': {'save': True},
                    'phone': {
                        'save': True,
                        'lists': {
                            'functionKey': {'save': True},
                            'phonebook': {'save': True},
                        },
                    },
                },
            },
        }
        self._backup(description)

    def backup_miniPabx(self, miniPabx):
        """Backup miniPabx configuration."""
        logger.info('backup miniPabx')

        root_dir = '/telephony/{0}/miniPabx/{1}'.format(self.group, miniPabx)
        description = {
            root_dir: {
                'save': True,
                'children': {
                    'hunting': {
                        'save': True,
                        'lists': {
                            'agent': {'save': True},
                        },
                    },
                    'tones': {'save': True},
                },
            },
        }
        self._backup(description)

    def backup_number(self, number):
        """Backup number configuration."""
        logger.info('backup number')

        root_dir = '/telephony/{0}/number/{1}'.format(self.group, number)
        description = {root_dir: {'save': True}}
        self._backup(description)

    def backup_ovhPabx(self, ovhPabx):
        """Backup ovhPabx configuration."""
        logger.info('backup ovhPabx')

        # basic informations
        root_dir = '/telephony/{0}/ovhPabx/{1}'.format(self.group, ovhPabx)
        description = {
            root_dir: {
                'save': True,
                'children': {
                    'hunting': {
                        'save': True,
                        'lists': {
                            'agent': {
                                'save': True,
                                'lists': {
                                    'queue': {'save': True},
                                },
                            },
                            'queue': {
                                'save': True,
                                'lists': {
                                    'agent': {'save': True},
                                },
                            },
                        },
                    },
                },
                'lists': {
                    'sound': {'save': True},
                    'tts': {'save': True},
                    'menu': {
                        'save': True,
                        'lists': {
                            'entry': {'save': True},
                        },
                    },
                    'dialplan': {
                        'save': True,
                        'lists': {
                            'extension': {
                                'save': True,
                                'lists': {
                                    'conditionScreenList': {'save': True},
                                    'conditionTime': {'save': True},
                                    'rule': {'save': True},
                                },
                            },
                        },
                    },
                },
            },
        }
        self._backup(description)

    def backup_phonebook(self, phonebook):
        """Backup phonebook configuration."""
        logger.info('backup phonebook')

        root_dir = '/telephony/{0}/phonebook/{1}'.format(self.group, phonebook)
        description = {
            root_dir: {
                'save': True,
                'lists': {
                    'phonebookContact': {'save': True},
                },
            },
        }
        self._backup(description)

    def backup_redirect(self, redirect):
        """Backup redirect configuration."""
        logger.info('backup redirect')

        root_dir = '/telephony/{0}/redirect/{1}'.format(self.group, redirect)
        description = {root_dir: {'save': True}}
        self._backup(description)

    def backup_scheduler(self, scheduler):
        """Backup scheduler configuration."""
        logger.info('backup scheduler')

        root_dir = '/telephony/{0}/scheduler/{1}'.format(self.group, scheduler)
        description = {root_dir: {'save': True}}
        self._backup(description)

    def backup_screen(self, screen):
        """Backup screen configuration."""
        logger.info('backup screen')

        root_dir = '/telephony/{0}/screen/{1}'.format(self.group, screen)
        description = {
            root_dir: {
                'save': True,
                'lists': {
                    'screenLists': {'save': True},
                }
            },
        }
        self._backup(description)

    def backup_service(self, service):
        """Backup service configuration."""
        logger.info('backup service')

        root_dir = '/telephony/{0}/service/{1}'.format(self.group, service)
        description = {
            root_dir: {
                'save': True,
                'children': {
                    'directory': {'save': True},
                }
            },
        }
        self._backup(description)

    def backup_timeCondition(self, timeCondition):
        """Backup timeCondition configuration."""
        logger.info('backup timeCondition')

        root_dir = '/telephony/{0}/timeCondition/{1}'.format(self.group, timeCondition)
        description = {
            root_dir: {
                'save': True,
                'lists': {
                    'condition': {'save': True},
                },
                'children': {
                    'options': {'save': True},
                },
            },
        }
        self._backup(description)

    def _get_url(self, url):
        """Handle exception."""
        data = None
        try:
            data = self.client.get(url)
        except ResourceNotFoundError:
            logger.warning('{0} is not available: ResourceNotFound'.format(url))
        except BadParametersError:
            logger.warning('{0} is not available: BadParameters'.format(url))
        except Exception as e:
            logger.warning('Unknow exception with {0}'.format(url))
            logger.exception(e)
        return data

    def _save_data(self, path):
        """Save data as yaml into backup_file."""

        url = path
        data_file = '{0}.yml'.format(path[11:])
        data = self._get_url(url)

        if not data:
            return

        destination = os.path.join(self.rootdir, data_file)
        logger.debug('saving to {0}'.format(destination))
        destination_dir = os.path.dirname(destination)

        if not os.path.isdir(destination_dir):
            os.makedirs(destination_dir)
            logger.debug('created dir {0}'.format(destination_dir))

        with open(destination, 'w') as outfile:
                yaml.safe_dump(data, outfile, default_flow_style=False)
        logger.debug('saving OK')


@click.command()
@click.option('--group', default=[], multiple=True,
              help='OVH billing account to backup.')
@click.option('--rootdir', default=get_default_dir(),
              help='Backup root dir.')
@click.option('--debug', default=False, is_flag=True)
def backup(group, rootdir, debug):
    """Backup OVH telephony settings using API."""

    if debug:
        logger.set_min_level_to_print(logging.DEBUG)
        logger.set_min_level_to_mail(None)
        logger.debug('debug activated')

    logger.info('Program start')

    # OVH Client
    client = ovh.Client()

    # First part check all groups
    # If specific group only, take this
    if len(group):
        groups = group
    else:
        groups = client.get('/telephony')

    logger.new_loop_logger()
    for group in groups:
        logger.new_iteration(prefix=group)
        manager = BackupManager(client, group, rootdir, logger)
        manager.backup()
    logger.del_loop_logger()


if __name__ == "__main__":
    try:
        backup()
    except Exception as e:
        logger.exception(e)
