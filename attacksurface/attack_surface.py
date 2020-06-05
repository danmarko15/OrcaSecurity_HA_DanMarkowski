import argparse
import logging
import os
from timeit import default_timer as timer

import cloud
import data_monitor
from flask import Flask, request, jsonify, make_response


def run_on_startup():
    logging.basicConfig(filename="attack_surface.log", level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %('
                               'threadName)s : %(message)s')
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("-ce", "--cloud", required=True, help="JSON of the cloud environment")
    args = vars(arg_parse.parse_args())
    cloud_env_cfg = args["cloud"]
    cloud.Cloud(cloud_env_cfg)
    data_monitor.DataMonitor()


class MyFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                run_on_startup()
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = MyFlaskApp(__name__)


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


if __name__ == '__main__':  # to run directly from python
    # app.run(host='0.0.0.0', debug=True)
    app.run()
