import cloud
from flask import current_app as app


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataMonitor(metaclass=Singleton):
    def __init__(self):
        cloud_env = cloud.Cloud()
        self.vm_count = cloud_env.vm_count
        self.request_count = 0
        self.avg_request_time = -1

    def log_new_request(self, start, end):
        """Log a new request made to the service, calculate average request time and count"""
        self.request_count += 1
        time = (end - start) * 1000
        if self.avg_request_time is not -1:
            self.avg_request_time = (self.avg_request_time + time) / self.request_count
        else:
            self.avg_request_time = time

        app.logger.info(f'Logged new request with time: {time}, new average is: {self.avg_request_time}')

    def get_stats(self):
        """Return current service stats: number of VM in the cloud, requests made and average request time """
        stat_dict = dict()
        stat_dict['vm_count'] = self.vm_count
        stat_dict['request_count'] = self.request_count
        stat_dict['average_request_time'] = self.avg_request_time

        return stat_dict
