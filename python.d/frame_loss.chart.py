import urllib3
from bases.FrameworkServices.UrlService import UrlService

ORDER = ['status', 'rooms']

SUCCESS = 'success'

CHARTS = {
    'status': {
        'options': ['Frame Loss Monitor', 'status', 'boolean', 'status', 'frame_loss.status', 'line'],
        'lines': [
            [SUCCESS, 'status', 'absolute']
        ]}
}


class Service(UrlService):
    def __init__(self, configuration=None, name=None):
        UrlService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.url = self.configuration.get('url')

    def _get_data(self):
        data = dict()

        data[SUCCESS] = 1

        # try:
        #     respose, status = self._get_raw_data_with_status(url=self.url)
        # except urllib3.exceptions.HTTPError:
        #     data[SUCCESS] = 0


        return data

    #
    # def _check_raw_data(self, data):
    #     """
    #     Check if all data has been gathered from socket.
    #     Parse first line containing message length and check against received message
    #     :param data: str
    #     :return: boolean
    #     """
    #     lines = data.split('\n')
    #     supposed = lines[0][1:-1]
    #
    #     if not supposed.isdigit():
    #         return True
    #
    #     supposed = int(supposed)
    #
    #     if len(lines) == supposed * 2 + 1 + 1:      # 1 beginning line and 1 trailing line
    #         self.debug("received full response from redis")
    #         return True
    #
    #     self.debug("waiting more data from redis")
    #     return False
    #
    # def check(self):
    #     data = self._get_data()
    #     if data is None:
    #         return False
    #
    #     for name in data:
    #         if name.endswith('-worker'):
    #             self.definitions['workers']['lines'].append([name, None, 'absolute'])
    #         else:
    #             self.definitions['queues']['lines'].append([name, None, 'absolute'])
    #
    #     return True
