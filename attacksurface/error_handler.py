import sys
from flask import current_app as app


class ErrorHandler:

    @staticmethod
    def handle_error(msg, error, sys_exit=False):
        app.logger.error(f'{msg} . err: {error}')
        if sys_exit:
            sys.exit(1)
