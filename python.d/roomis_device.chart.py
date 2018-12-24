# -*- coding: utf-8 -*-
import urllib3
import re

import json
from datetime import datetime
from datetime import timedelta

try:
    from time import monotonic as time
except ImportError:
    from time import time

from bases.FrameworkServices.UrlService import UrlService

# default module values (can be overridden per job in `config`)
update_every = 3
priority = 60000
retries = 60

ONLINE = 'On line device'
OFFLINE = 'Off line device'

# Status dimensions
ORDER = ['on_line', 'off_line']

CHARTS = {
    'on_line': {
        'options': [None, 'On line device', 'units', 'count', 'roomis_device.on_line', 'line'],
        'lines': [
            [ONLINE, 'no connection', 'absolute']
        ]},
    'off_line': {
        'options': [None, 'Off line device', 'units', 'count', 'roomis_device.off_line', 'line'],
        'lines': [
            [OFFLINE, 'no connection', 'absolute']
        ]
    }
}


class Service(UrlService):
    def __init__(self, configuration=None, name=None):
        UrlService.__init__(self, configuration=configuration, name=name)
        self.url = self.configuration.get('url')
        self.follow_redirect = self.configuration.get('redirect', True)
        self.order = ORDER
        self.definitions = CHARTS

    def _get_data(self):

        data = dict()
        try:
            status, content = self._get_raw_data_with_status(retries=1 if self.follow_redirect else False,
                                                             redirect=self.follow_redirect)
            content = json.loads(content)

            data[ONLINE] = content['on']
            data[OFFLINE] = content['off']
        except ConnectionError:
            return None
        return data
