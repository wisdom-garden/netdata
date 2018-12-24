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

# Response
HTTP_RESPONSE_TIME = 'time'

# Status dimensions
HTTP_SUCCESS = 'success'
HTTP_BAD_CONTENT = 'bad_content'
HTTP_BAD_STATUS = 'bad_status'
HTTP_TIMEOUT = 'timeout'
HTTP_NO_CONNECTION = 'no_connection'

ORDER = ['status', 'dag_status']

DAG_SUCCESS = 'dag_success'
DAG_TIMEOUT = 'dag_timeout'

CHARTS = {
    'status': {
        'options': [None, 'HTTP status', 'boolean', 'status', 'core_data.status', 'line'],
        'lines': [
            [HTTP_SUCCESS, 'success', 'absolute'],
            [HTTP_BAD_CONTENT, 'bad content', 'absolute'],
            [HTTP_BAD_STATUS, 'bad status', 'absolute'],
            [HTTP_TIMEOUT, 'connect timout', 'absolute'],
            [HTTP_NO_CONNECTION, 'no connection', 'absolute']
        ]},
    'dag_status': {
        'options': [None, 'Dag status', 'boolean', 'dag_status', 'core_data.dag_status', 'line'],
        'lines': [
            [DAG_SUCCESS, 'dag success', 'absolute'],
            [DAG_TIMEOUT, 'dag timeout', 'absolute']
        ]
    }
}


class Service(UrlService):
    def __init__(self, configuration=None, name=None):
        UrlService.__init__(self, configuration=configuration, name=name)
        pattern = self.configuration.get('regex')
        self.regex = re.compile(pattern) if pattern else None
        self.status_codes_accepted = self.configuration.get('status_accepted', [200])
        self.follow_redirect = self.configuration.get('redirect', True)
        self.order = ORDER
        self.definitions = CHARTS

    def _get_data(self):
        """
        Format data received from http request
        :return: dict
        """
        data = dict()
        data[HTTP_SUCCESS] = 0
        data[HTTP_BAD_CONTENT] = 0
        data[HTTP_BAD_STATUS] = 0
        data[HTTP_TIMEOUT] = 0
        data[HTTP_NO_CONNECTION] = 0
        data[DAG_SUCCESS] = 0
        data[DAG_TIMEOUT] = 0

        url = self.url

        try:
            start = time()
            status, content = self._get_raw_data_with_status(retries=1 if self.follow_redirect else False,
                                                             redirect=self.follow_redirect)
            diff = time() - start

            data[HTTP_RESPONSE_TIME] = max(round(diff * 10000), 0)

            self.debug('Url: {url}. Host responded with status code {code} in {diff} s'.format(
                url=url, code=status, diff=diff
            ))

            self.process_response(content, data, status)

        # except urllib3.exceptions.NewConnectionError as error:
        #     self.debug("Connection failed: {url}. Error: {error}".format(url=url, error=error))
        #     data[HTTP_NO_CONNECTION] = 1

        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.PoolError) as error:
            self.debug("Connection timed out: {url}. Error: {error}".format(url=url, error=error))
            data[HTTP_TIMEOUT] = 1

        except urllib3.exceptions.HTTPError as error:
            self.debug("Connection failed: {url}. Error: {error}".format(url=url, error=error))
            data[HTTP_NO_CONNECTION] = 1

        except (TypeError, AttributeError) as error:
            self.error('Url: {url}. Error: {error}'.format(url=url, error=error))
            return None
        return data

    def process_response(self, content, data, status):
        self.debug('Content: \n{content}\n'.format(content=content))

        if status in self.status_codes_accepted:
            data[HTTP_SUCCESS] = 1
        else:
            data[HTTP_BAD_STATUS] = 1

        for status in json.loads(content)['response']['dag_runs']:

            if status['state'] != 'failed':
                data[DAG_SUCCESS] = 1
            else:
                data[DAG_SUCCESS] = 0
                break

        for dag_times in json.loads(content)['response']['dag_runs']:
            now = datetime.now()
            dag_time = datetime.strptime(dag_times['start_date'], '%Y-%m-%d %H:%M:%S.%f')
            if now - dag_time > timedelta(hours=25):
                data[DAG_TIMEOUT] = 1
                break
            else:
                data[DAG_TIMEOUT] = 0
