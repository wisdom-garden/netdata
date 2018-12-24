# -*- coding: utf-8 -*-
# Description:  varnish netdata python.d module
# Author: l2isbad
from bases.FrameworkServices.ExecutableService import ExecutableService


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

    def _get_data(self):
        """
        Format data received from shell command
        :return: dict
        """
        data = dict()
        data['folder_status'] = 1 if self._get_raw_data(stderr=True) else 0

        return data
