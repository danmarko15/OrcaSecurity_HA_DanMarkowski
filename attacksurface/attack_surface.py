import argparse
import logging
import cloud
from flask import Flask, request, jsonify, make_response
import os
import json

# app = Flask(__name__)


# @app.before_first_request
def run_on_startup():
    # TODO config?
    # TODO log
    logging.basicConfig(filename="attack_surface.log", level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %('
                               'threadName)s : %(message)s')
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("-ce", "--cloud", required=True, help="JSON of the cloud environment")
    args = vars(arg_parse.parse_args())
    cloud_env_cfg = args["cloud"]
    cloud_env = cloud.Cloud(cloud_env_cfg)
    cloud_env.init_cloud_env()


class MyFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                run_on_startup()
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = MyFlaskApp(__name__)


@app.route('/api/v1.0/attack', methods=['GET'])
def attack():
    vm_id = request.args.get('vm_id')
    app.logger.info(f'New attack request for VM: {vm_id}')
    cloud_env = cloud.Cloud()
    vm_list = cloud_env.vulnerable_to(vm_id)
    return make_response(jsonify(list(vm_list)), 200)

    # TODO if no vm_id passed?
    # TODO if vm_id doesn't exists?


if __name__ == '__main__':  # to run directly from python
    # app.run(host='0.0.0.0', debug=True)
    app.run()
