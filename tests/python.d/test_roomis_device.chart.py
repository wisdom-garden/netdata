import os
from bases.loaders import ModuleAndConfigLoader


PYTHON_MODULES_DIR = os.path.abspath(__file__ + '/../../../python.d')
loader = ModuleAndConfigLoader()
mod = loader.load_module_from_file("roomis_device", PYTHON_MODULES_DIR + '/' + 'roomis_device.chart.py')[0]


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
        'url': 'https://easy-mock.com/mock/5c2058ef0fd1077df5e6e8d0/nfls/device-health'
    }

    config.update(BASE_CONFIG)
    print(config)

    service = mod.Service(config)
    service.logger.severity = 'DEBUG'
    print("check: {}".format(service.check()))
    print("create: {}".format(service.create()))
    print("update: {}".format(service.update(1)))
