import argparse
import logging
import os

import cloud
import data_monitor
from flask import Flask


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


class FlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                run_on_startup()
        super(FlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)
