from bases.FrameworkServices.SocketService import SocketService

ORDER = ['workers', 'queues']

CHARTS = {
    'workers': {
        'options': [None, 'resque workers', 'workers', 'workers', 'resque.workers', 'line'],
        'lines': [
            # lines are created dynamically in `check()` method
        ]},
    'queues': {
        'options': [None, 'resque queues', 'jobs', 'queues', 'resque.queues', 'line'],
        'lines': [
            # lines are created dynamically in `check()` method
        ]},
}


class Service(SocketService):
    def __init__(self, configuration=None, name=None):
        SocketService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self._keep_alive = True
        self.host = self.configuration.get('host', 'localhost')
        self.port = self.configuration.get('port', 6379)
        self.unix_socket = self.configuration.get('socket')
        password = self.configuration.get('pass', str())
        self.auth_request = 'AUTH {}\r\n'.format(password).encode() if password else None

    def _get_data(self):
        if self.auth_request:
            self.request = self.auth_request
            raw = self._get_raw_data().strip()
            if raw != "+OK":
                self.error("invalid password")
                return None

        self.request = 'KEYS resque:worker:node:*:started\r\nSMEMBERS resque:queues\r\n'.encode()
        response = self._get_raw_data()

        if response is None:
            # error has already been logged
            return None

        try:
            parsed = response.split("\r\n")
        except AttributeError:
            self.error("response is invalid/empty")
            return None

        data = dict()
        queues = []
        for line in parsed:
            if not line or line[0] == '$' or line[0] == '*':
                continue

            if ':' in line:     # worker has pattern of 'node:pid:name'
                worker = line.split(':')[4] + '_worker'
                if worker in data:
                    data[worker] += 1
                else:
                    data[worker] = 1
            else:
                queues.append(line)

        # make another request to get queue length
        self.request = ''.join(['LLEN resque:queue:{}\r\n'.format(q) for q in queues]).encode()
        response = self._get_raw_data()

        if response is None:
            # error has already been logged
            return None

        try:
            parsed = response.split("\r\n")
        except AttributeError:
            self.error("response is invalid/empty")
            return None

        for idx, q in enumerate(queues):
            data[q] = parsed[idx][1:]     # integer is prefixed with ':'

        return data

    def _check_raw_data(self, data):
        """
        Check if all data has been gathered from socket.
        Parse first line containing message length and check against received message
        :param data: str
        :return: boolean
        """
        length = len(data)
        supposed = data.split('\n')[0][1:-1]
        offset = len(supposed) + 4  # 1 dollar sing, 1 new line character + 1 ending sequence '\r\n'
        if not supposed.isdigit():
            return True
        supposed = int(supposed)

        if length - offset >= supposed:
            self.debug("received full response from redis")
            return True

        self.debug("waiting more data from redis")
        return False

    def check(self):
        data = self._get_data()
        if data is None:
            return False

        for name in data:
            if name.endswith('_worker'):
                self.definitions['workers']['lines'].append([name, None, 'absolute'])
            else:
                self.definitions['queues']['lines'].append([name, None, 'absolute'])

        return True
