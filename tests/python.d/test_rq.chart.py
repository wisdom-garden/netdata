import imp
import os

PYTHON_MODULES_DIR = os.path.abspath(__file__ + '/../../../python.d')

with open(os.path.join(PYTHON_MODULES_DIR, 'rq.chart.py'), 'rb') as fp:
    rq_chart = imp.load_module('rq_chart', fp, 'rq.chart.py', ('.py', 'rb', imp.PY_SOURCE))


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
        "rq_dashboard": 'http://localhost:9181'
    }

    config.update(BASE_CONFIG)
    print(config)

    service = rq_chart.Service(config)
    # print(service.logger.severity)
    service.logger.severity = 'DEBUG'
    print("check: {}".format(service.check()))
    print("create: {}".format(service.create()))
    print('----------------- first update -----------------')
    service.update(interval=1000000)
    print('----------------- second update -----------------')
    service.update(interval=1000000)
