# -*- coding: utf-8 -*-

import json
import threading

from collections import namedtuple

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from bases.FrameworkServices.UrlService import UrlService

METHODS = namedtuple('METHODS', ['get_data', 'url', 'run'])

SUCCESS = 'success'

ERROR = [
    'login.state',
    'login.error_code',
    'get_work_state.state',
    'get_work_state.error_code',
    'device_state.state',
    'device_state.error_code',
    'disks.state',
    'disks.error_count',
    'channels.state',
    'channels.error_count'
]

ORDER = ['state', 'login', 'get_work_state', 'device_state', 'disks', 'channels']

CHARTS = {
    'state': {
        'options': [None, 'state', 'state', 'state', 'nvr.state', 'line'],
        'lines': [
            ['login_state', 'login', 'absolute'],
            ['get_work_state_state', 'work', 'absolute'],
            ['device_state_state', 'device', 'absolute'],
            ['disks_state', 'disk', 'absolute'],
            ['channels_state', 'channel', 'absolute']
        ]
    },
    'login': {
        'options': [None, 'login', 'code', 'login', 'nvr.login', 'line'],
        'lines': [
            ['login_error_code', 'error_code', 'absolute']
        ]
    },
    "get_work_state": {
        'options': [None,  'get work state', 'code', 'get work state', 'nvr.get_work_state', 'line'],
        'lines': [
            ['get_work_state_error_code', 'error code', 'absolute']
        ]
    },
    "device_state": {
        'options': [None,  'device state', 'code', 'device state', 'nvr.device_state', 'line'],
        'lines': [

            ['work_state_error_code', 'error code', 'absolute']
        ]
    },
    "disks": {
        'options': [None,  'disks', 'count', 'disks', 'nvr.disks', 'line'],
        'lines': [

            ['disks_error_count', 'error disks', 'absolute']
        ]
    },
    "channels": {
        'options': [None,  'channels', 'count', 'channels', 'nvr.channels', 'line'],
        'lines': [
            ['channels_error_count', 'error channels', 'absolute']
        ]
    },
}


class Service(UrlService):
    def __init__(self, configuration=None, name=None):
        UrlService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.api_host = self.configuration.get('api_host')
        self.api_port = self.configuration.get('api_port', 9600)
        self.device_host = self.configuration.get('device_host')
        self.device_port = self.configuration.get('device_port')
        self.username = self.configuration.get('username', 'admin')
        self.password = self.configuration.get('password')
        self.channels = self.configuration.get('channels')
        self.url = '{scheme}://{host}:{port}'.format(scheme=self.configuration.get('scheme', 'http'),
                                                     host=self.api_host,
                                                     port=self.api_port)
        self.methods = [METHODS(get_data=self._get_node_stats,
                                url=self.url + '/api/check?host={host}&port={port}&username={user}&password={password}&channels={channels}'.format(
                                    host=self.device_host,
                                    port=self.device_port,
                                    user=self.username,
                                    password=self.password,
                                    channels=self.channels),
                                run=self.configuration.get('node_stats', True))]

    def _get_data(self):
        threads = list()
        queue = Queue()
        result = dict()

        for method in self.methods:
            if not method.run:
                continue
            th = threading.Thread(target=method.get_data,
                                  args=(queue, method.url))
            th.start()
            threads.append(th)

        for thread in threads:
            thread.join()
            result.update(queue.get())

        return result or None

    def _get_node_stats(self, queue, url):

        raw_data = self._get_raw_data(url)

        if not raw_data:
            return queue.put(dict())

        data = json.loads(raw_data)

        to_netdata = fetch_data_(raw_data=data,
                                 metrics=ERROR)

        return queue.put(to_netdata)


def fetch_data_(raw_data, metrics):
    data = dict()

    for metric in metrics:
        value = raw_data
        metrics_list = metric.split('.')
        try:
            for m in metrics_list:
                value = value[m]
        except KeyError:
            continue

        if value == 'unknown':
            pass
        elif not value:
            data['_'.join(metrics_list)] = 0
        else:
            data['_'.join(metrics_list)] = value

    return data