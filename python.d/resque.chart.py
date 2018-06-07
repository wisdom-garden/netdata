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
        self.db = self.configuration.get('db', None)
        self.password = self.configuration.get('pass', str())

    def _get_data(self):
        if self.password:
            self.request = 'AUTH {}\r\n'.format(self.password).encode()
            raw = self._get_raw_data().strip()
            if raw != "+OK":
                self.error("invalid password")
                return None

        if self.db:
            self.request = 'SELECT {}\r\n'.format(self.db).encode()
            # self.request = 'INFO\r\n'.encode()
            raw = self._get_raw_data().strip()
            if raw != "+OK":
                self.error("invalid db index")
                return None


        self.request = 'KEYS resque:worker:node:*:started\r\n'.encode()
        response_worker = self._get_raw_data()

        self.request = 'SMEMBERS resque:queues\r\n'.encode()
        response_queue = self._get_raw_data()

        response = response_worker + response_queue

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
                worker = line.split(':')[4] + '-worker'
                if worker in data:
                    data[worker] += 1
                else:
                    data[worker] = 1
            else:
                queues.append(line)
                data[line] = 0

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
        lines = data.split('\n')
        supposed = lines[0][1:-1]

        if not supposed.isdigit():
            return True

        supposed = int(supposed)

        if len(lines) == supposed * 2 + 1 + 1:      # 1 beginning line and 1 trailing line
            self.debug("received full response from redis")
            return True

        self.debug("waiting more data from redis")
        return False

    def check(self):
        data = self._get_data()
        if data is None:
            return False

        for name in data:
            if name.endswith('-worker'):
                self.definitions['workers']['lines'].append([name, None, 'absolute'])
            else:
                self.definitions['queues']['lines'].append([name, None, 'absolute'])

        return True
