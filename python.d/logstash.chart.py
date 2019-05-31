# -*- coding: utf-8 -*-

import json
import threading

from collections import namedtuple

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from bases.FrameworkServices.UrlService import UrlService

update_every = 5

METHODS = namedtuple('METHODS', ['get_data', 'url', 'run'])

NODE_STATS = [
    'jvm.gc.collectors.young.collection_count',
    'jvm.gc.collectors.old.collection_count',
    'jvm.gc.collectors.young.collection_time_in_millis',
    'jvm.gc.collectors.old.collection_time_in_millis',
    'jvm.mem.heap_used_percent',
    'jvm.mem.heap_used_in_bytes',
    'jvm.mem.heap_committed_in_bytes',
    'process.max_file_descriptors',
    'process.open_file_descriptors'
]

ORDER = ['jvm_mem_heap', 'jvm_mem_heap_bytes', 'jvm_gc_count', 'jvm_gc_time']


CHARTS = {
    'jvm_mem_heap': {
        'options': [None, 'JVM Heap Percentage Currently in Use', 'percent', 'memory usage and gc',
                    'logstash.jvm_heap', 'area'],
        'lines': [
            ['jvm_mem_heap_used_percent', 'inuse', 'absolute']
        ]},
    'jvm_mem_heap_bytes': {
        'options': [None, 'JVM Heap Commit And Usage', 'MB', 'memory usage and gc',
                    'logstash.jvm_heap_bytes', 'area'],
        'lines': [
            ['jvm_mem_heap_committed_in_bytes', 'commited', 'absolute', 1, 1048576],
            ['jvm_mem_heap_used_in_bytes', 'used', 'absolute', 1, 1048576]
        ]},
    'jvm_gc_count': {
        'options': [None, 'Garbage Collections', 'counts', 'memory usage and gc', 'logstash.gc_count', 'stacked'],
        'lines': [
            ['jvm_gc_collectors_young_collection_count', 'young', 'incremental'],
            ['jvm_gc_collectors_old_collection_count', 'old', 'incremental']
        ]},
    'jvm_gc_time': {
        'options': [None, 'Time Spent On Garbage Collections', 'ms', 'memory usage and gc',
                    'logstash.gc_time', 'stacked'],
        'lines': [
            ['jvm_gc_collectors_young_collection_time_in_millis', 'young', 'incremental'],
            ['jvm_gc_collectors_old_collection_time_in_millis', 'old', 'incremental']
        ]}
}

class Service(UrlService):
    def __init__(self, configuration=None, name=None):
        UrlService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.host = self.configuration.get('host')
        self.port = self.configuration.get('port', 9600)
        self.url = '{scheme}://{host}:{port}'.format(scheme=self.configuration.get('scheme', 'http'),
                                                     host=self.host,
                                                     port=self.port)
        self.methods = [METHODS(get_data=self._get_node_stats,
                                url=self.url + '/_node/stats/jvm?pretty',
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
                                 metrics=NODE_STATS)

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
        data['_'.join(metrics_list)] = value
    return data
