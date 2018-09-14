# -*- coding: utf-8 -*-
# Description:  varnish netdata python.d module
# Author: l2isbad
from bases.FrameworkServices.ExecutableService import ExecutableService
from subprocess import Popen


class Service(ExecutableService):
    def __init__(self, configuration=None, name=None):
        ExecutableService.__init__(self, configuration=configuration, name=name)
        self.order = [self.configuration.get('mount_folder', 'mount_folder')]
        self.definitions = {
            self.configuration.get('mount_folder', 'mount_folder'): {
                'options': [None, 'monitor_nfs_mount_folder', 'folders', 'folders', 'mount.folders', 'line'],
                'lines': [
                    ['folder_status', None, 'absolute']
                ]
            }
        }
        self.file_path = self.configuration.get('file_path')

    def _get_data(self):
        """
        Format data received from shell command
        :return: dict
        """
        return_code = self._get_raw_data()

        data = dict()
        data['folder_status'] = return_code

        return data

    def _get_raw_data(self, stderr=False):
        """
        Get result from executed command, 0 means succeed, 1 means failed
        """
        try:
            p = Popen([self.configuration.get('command', 'touch'), self.file_path])
        except Exception as error:
            self.error('Executing command touch file resulted in error: {error}'.format(error=error))
            return_code = p.wait()
        else:
            return_code = p.wait()

        return return_code
