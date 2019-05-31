import os
from bases.loaders import ModuleAndConfigLoader


PYTHON_MODULES_DIR = os.path.abspath(__file__ + '/../../../python.d')
loader = ModuleAndConfigLoader()
mod = loader.load_module_from_file("httpcheck", PYTHON_MODULES_DIR + '/' + 'httpcheck.chart.py')[0]


if __name__ == '__main__':
    BASE_CONFIG = {
        'update_every': os.getenv('NETDATA_UPDATE_EVERY', 1),
        'retries': 60,
        'priority': 60000,
        'autodetection_retry': 0,
        'chart_cleanup': 10,
        'name': 'roomis_device'
    }

    config = {
        'job_name': 'roomis_device',
        'timeout': 10,
        "override_name": "roomis_device",
        'url': 'http://www.baidu.com'
    }

    config.update(BASE_CONFIG)
    print(config)

    service = mod.Service(config)
    service.logger.severity = 'DEBUG'
    print("check: {}".format(service.check()))
    print("create: {}".format(service.create()))
    print("update: {}".format(service.update(1)))
