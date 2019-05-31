import os
from bases.loaders import ModuleAndConfigLoader


PYTHON_MODULES_DIR = os.path.abspath(__file__ + '/../../../python.d')
loader = ModuleAndConfigLoader()
mod = loader.load_module_from_file("nvr", PYTHON_MODULES_DIR + '/' + 'nvr.chart.py')[0]


if __name__ == '__main__':
    BASE_CONFIG = {
        'update_every': os.getenv('NETDATA_UPDATE_EVERY', 1),
        'retries': 60,
        'priority': 60000,
        'autodetection_retry': 0,
        'chart_cleanup': 10,
        'name': 'nvr'
    }

    config = {
        'job_name': 'nvr',
        'timeout': 10,
        "override_name": 'nvr',
        'api_host': '120.27.105.241',
        'api_port': '28000',
        'device_host': '120.27.105.241',
        'device_port': '18000',
        'username': 'admin',
        'password': 'MAeo9HwRu',
        'channels': '33,34,35,36,38'
    }

    config.update(BASE_CONFIG)
    print(config)

    service = mod.Service(config)
    service.logger.severity = 'DEBUG'
    print("check: {}".format(service.check()))
    print("create: {}".format(service.create()))
    print("update: {}".format(service.update(1)))
