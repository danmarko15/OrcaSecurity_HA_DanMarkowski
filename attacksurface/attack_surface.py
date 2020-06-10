from timeit import default_timer as timer

import cloud
import data_monitor
import flask_app
from flask import request, jsonify, make_response
from error_handler import ErrorHandler

app = flask_app.FlaskApp(__name__)


@app.route('/api/v1.0/attack', methods=['GET'])
def attack():
    """Return the VM ids that can potentially attack 'vm_id'"""
    start = timer()
    monitor = data_monitor.DataMonitor()

    vm_id = request.args.get('vm_id')
    if not vm_id:
        raise ValueError('Query parameter vm_id was not provided')
    app.logger.info(f'New attack request for VM: {vm_id}')

    cloud_env = cloud.Cloud()
    vm_list = cloud_env.vulnerable_to(vm_id)

    end = timer()
    monitor.log_new_request(start, end)
    return make_response(jsonify(list(vm_list)), 200)


@app.route('/api/v1.0/stats', methods=['GET'])
def stats():
    """Return current service stats: number of VM in the cloud, requests made and average request time """
    app.logger.info(f'New stats request received')
    start = timer()
    monitor = data_monitor.DataMonitor()
    current_stats = monitor.get_stats()
    end = timer()
    monitor.log_new_request(start, end)

    return make_response(jsonify(current_stats), 200)


@app.errorhandler(Exception)
def handle_exception(error):
    ErrorHandler.handle_error('The server encountered an error', error)
    return make_response(jsonify({'error': "The server encountered an error and failed to process your request"}), 400)


@app.errorhandler(ValueError)
def handle_exception(error):
    ErrorHandler.handle_error('The server encounter a ValueError', error)
    return make_response(jsonify({'error': "The server could not process request, please check your input data"}), 400)


if __name__ == '__main__':
    app.run()
