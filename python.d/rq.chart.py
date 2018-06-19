from bases.FrameworkServices.SocketService import SocketService

ORDER = ['schedulers', 'workers', 'queues']

CHARTS = {
    'schedulers': {
        'options': [None, 'rq schedulers', 'scheduler', 'schedulers', 'rq:schedulers', 'line'],
        'lines': [
            # lines are created dynamically in `check()` method
        ]},

    'workers': {
        'options': [None, 'rq workers', 'worker', 'workers', 'rq:workers', 'line'],
        'lines': [
            # lines are created dynamically in `check()` method
        ]},

    'queues': {
        'options': [None, 'rq queues', 'queue', 'queues', 'rq:queues', 'line'],
        'lines': [
            # lines are created dynamically in `check()` method
        ]}
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

        data = dict()

        self.request = 'ZCARD rq:scheduler:scheduled_jobs\r\n'.encode()
        response_scheduled = self._get_raw_data()
        if response_scheduled:
            data['scheduler-jobs'] = response_scheduled[1]

        self.request = 'KEYS rq:worker:*\r\n'.encode()
        response_worker = self._get_raw_data()

        if response_worker:
            try:
                parsed = response_worker.split("\r\n")
            except AttributeError:
                self.error("response is invalid/empty")
                return None

            for line in parsed:
                if not line or line[0] == '$' or line[0] == '*':
                    continue

                if ':' in line:     # worker has pattern of 'node:pid:name'
                    worker = line.split(':')[2].split('.')[0] + '-worker'
                    if worker in data:
                        data[worker] += 1
                    else:
                        data[worker] = 1
                else:
                    data[line] = 0

        self.request = 'SMEMBERS rq:queues\r\n'.encode()
        response_queue = self._get_raw_data()

        if response_queue:
            try:
                parsed = response_queue.split("\r\n")
            except AttributeError:
                self.error("response is invalid/empty")
                return None

            for line in parsed:
                if not line or line[0] == '$' or line[0] == '*':
                    continue

                if ':' in line:     # worker has pattern of 'node:pid:name'
                    queue = line.split(':')[2] + '-queue'
                    if queue in data:
                        data[queue] += self._get_number_for_queue(line)
                    else:
                        data[queue] = self._get_number_for_queue(line)

        return data

    def _get_number_for_queue(self, queue_name):
        self.request = 'LLEN {}\r\n'.format(queue_name).encode()
        raw = self._get_raw_data()
        return raw[1]

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
            elif name.endswith('-queue'):
                self.definitions['queues']['lines'].append([name, None, 'absolute'])
            else:
                self.definitions['schedulers']['lines'].append([name, None, 'absolute'])
        return True
