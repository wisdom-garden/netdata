import json

from bases.FrameworkServices.UrlService import UrlService

ORDER = ['queues']

CHARTS = {
    'queues': {
        'options': [None, 'RQ Job Queues', 'jobs', 'localhost', 'rq.jobs', 'line'],
        'lines': [
            ['default', 'default', 'absolute']
        ]}
}


class Service(UrlService):
    def __init__(self, configuration=None, name=None):
        UrlService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.url = configuration.get('rq_dashboard') + '/queues.json'

    def _get_data(self):
        """
        Format data received from shell command
        :return: dict
        """
        try:
            raw_data = self._get_raw_data()

            if not raw_data:
                return {'default': 0}

            parsed = json.loads(raw_data)
            data = {}
            for queue in parsed['queues']:
                data[queue['name']] = queue['count']

            return data
        except (ValueError, AttributeError):
            return None
