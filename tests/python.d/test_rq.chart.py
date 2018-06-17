import os
from bases.loaders import ModuleAndConfigLoader


PYTHON_MODULES_DIR = os.path.abspath(__file__ + '/../../../python.d')
loader = ModuleAndConfigLoader()
mod = loader.load_module_from_file("rq", PYTHON_MODULES_DIR + '/' + 'rq.chart.py')[0]


if __name__ == '__main__':
    BASE_CONFIG = {
        'update_every': os.getenv('NETDATA_UPDATE_EVERY', 1),
        'retries': 60,
        'priority': 60000,
        'autodetection_retry': 0,
        'chart_cleanup': 10,
        'name': str()
    }

    config = {
        "job_name": "localhost",
        "override_name": None,
        "db": 0
    }

    config.update(BASE_CONFIG)
    print(config)

    service = mod.Service(config)
    # print(service.logger.severity)
    service.logger.severity = 'DEBUG'
    print("check: {}".format(service.check()))
    print("create: {}".format(service.create()))
    print('----------------- first update -----------------')
    service.update(interval=1000000)
    print('----------------- second update -----------------')
    service.update(interval=1000000)
