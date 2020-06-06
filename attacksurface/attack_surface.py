from timeit import default_timer as timer

import cloud
import data_monitor
import flask_app
from flask import request, jsonify, make_response

app = flask_app.FlaskApp(__name__)


@app.route('/api/v1.0/attack', methods=['GET'])
def attack():
    start = timer()
    monitor = data_monitor.DataMonitor()

    vm_id = request.args.get('vm_id')
    app.logger.info(f'New attack request for VM: {vm_id}')

    cloud_env = cloud.Cloud()
    vm_list = cloud_env.vulnerable_to(vm_id)

    end = timer()
    monitor.log_new_request(start, end)
    return make_response(jsonify(list(vm_list)), 200)


@app.route('/api/v1.0/stats', methods=['GET'])
def stats():
    start = timer()
    monitor = data_monitor.DataMonitor()
    current_stats = monitor.get_stats()
    end = timer()
    monitor.log_new_request(start, end)

    return make_response(jsonify(current_stats), 200)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True)
    app.run()
