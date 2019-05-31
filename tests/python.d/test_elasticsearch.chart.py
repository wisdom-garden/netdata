import os
from bases.loaders import ModuleAndConfigLoader


PYTHON_MODULES_DIR = os.path.abspath(__file__ + '/../../../python.d')
loader = ModuleAndConfigLoader()
mod = loader.load_module_from_file("elasticsearch", PYTHON_MODULES_DIR + '/' + 'elasticsearch.chart.py')[0]


if __name__ == '__main__':
    BASE_CONFIG = {
        'update_every': os.getenv('NETDATA_UPDATE_EVERY', 1),
        'retries': 60,
        'priority': 60000,
        'autodetection_retry': 0,
        'chart_cleanup': 10,
        'name': 'logstash'
    }

    config = {
        'job_name': 'logstash',
        'timeout': 10,
        "override_name": "logstash",
        'host': 'elastic.roomis.com.cn',
        'scheme': 'https',
        'port': 443,
        'user': 'elastic',
        'pass': 'uh6ufC3EkjdqFJK4'
    }

    config.update(BASE_CONFIG)
    print(config)

    service = mod.Service(config)
    service.logger.severity = 'DEBUG'
    print("check: {}".format(service.check()))
    print("create: {}".format(service.create()))
    print("update: {}".format(service.update(1)))
