import os
from bases.loaders import ModuleAndConfigLoader


PYTHON_MODULES_DIR = os.path.abspath(__file__ + '/../../../python.d')
loader = ModuleAndConfigLoader()
mod = loader.load_module_from_file("core_data", PYTHON_MODULES_DIR + '/' + 'core_data.chart.py')[0]


if __name__ == '__main__':
    BASE_CONFIG = {
        'update_every': os.getenv('NETDATA_UPDATE_EVERY', 1),
        'retries': 60,
        'priority': 60000,
        'autodetection_retry': 0,
        'chart_cleanup': 10,
        'name': 'core_data'
    }

    config = {
        'job_name': 'core_data',
        'timeout': 10,
        "override_name": "localhost",
        'url': 'http://localhost:8801/api/v1/latest_runs'
    }

    config.update(BASE_CONFIG)
    print(config)

    service = mod.Service(config)
    service.logger.severity = 'DEBUG'
    print("check: {}".format(service.check()))
    print("create: {}".format(service.create()))
    print("update: {}".format(service.update(1)))
