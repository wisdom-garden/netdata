import os
import imp


PYTHON_MODULES_DIR = os.path.abspath(__file__ + '/../../../python.d')

print(PYTHON_MODULES_DIR)


with open(os.path.join(PYTHON_MODULES_DIR, 'redis.chart.py'), 'rb') as fp:
    redis_chart = imp.load_module(
        'redis_chart', fp, 'redis.chart.py',
        ('.py', 'rb', imp.PY_SOURCE)
    )

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
        "host": '127.0.0.1'
    }

    config.update(BASE_CONFIG)
    print(config)

    service = redis_chart.Service(config)
    # print(service.logger.severity)
    service.logger.severity = 'DEBUG'
    print(service.create())
    print('----------------- first update -----------------')
    print(service.update(interval=1000000))
    print('----------------- second update -----------------')
    print(service.update(interval=1000000))
