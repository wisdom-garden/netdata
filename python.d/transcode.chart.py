# -*- coding: utf-8 -*-

import json
from bases.FrameworkServices.UrlService import UrlService

# default module values (can be overridden per job in `config`)
update_every = 30
priority = 60000
retries = 60

# Status dimensions
ORDER = ['transcode']

CHARTS = {
    'transcode': {
        'options': [None, 'transcode monitor', 'count', 'transcode monitor', 'transcode.transcode', 'line'],
        'lines': [
            ['count', 'count', 'absolute'],
            ['fail_count', 'fail_count', 'absolute'],
            ['finish_count', 'finish_count', 'absolute'],
            ['process_count', 'process_count', 'absolute'],
            ['wait_process_count', 'wait_process_count', 'absolute'],
            ['schedule_count', 'schedule_count', 'absolute']
        ]}
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
            data['count'] = content['capture_count']
            data['fail_count'] = content['capture_fail_count']
            data['finish_count'] = content['capture_finish_count']
            data['process_count'] = content['capture_process_count']
            data['wait_process_count'] = content['capture_process_count']
            data['schedule_count'] = content['schedule_count']

        except:
            return None
        return data
