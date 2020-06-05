import json
from flask import current_app as app
import timeit

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Cloud(metaclass=Singleton):
    def __init__(self, cloud_env_cfg=None):
        if cloud_env_cfg:
            with open(cloud_env_cfg) as cloud_json_cfg:
                cloud_env = json.load(cloud_json_cfg)
                self.__vms_cfg = cloud_env["vms"]
                self.vm_count = len(self.__vms_cfg)
                self.__fw_rules = cloud_env["fw_rules"]
                self.__init_cloud_env()

            # TODO log

    def __init_cloud_env(self):
        # TODO logs, try/catch
        app.logger.info(f'initializing the cloud environment')
        # log 'init vms'
        self.__config_tag_to_vms()
        # log 'init fw rules'
        self.__config_dtag_to_stag()
        # log 'init vms'
        self.__config_vm_to_vms()

    # tag -> vm_ids
    # use the VM config
    def __config_tag_to_vms(self):
        app.logger.info(f'initializing the tag_to_vms config')
        tag_to_vms = {}
        for vm in self.__vms_cfg:
            for tag in vm["tags"]:
                if tag in tag_to_vms:
                    tag_to_vms[tag].add(vm["vm_id"])
                else:
                    tag_to_vms[tag] = {vm["vm_id"]}
        self.tag_to_vms = tag_to_vms
        app.logger.info(f'Configured tag_to_vms: {tag_to_vms}')

    # dest tag -> source tag
    # use the FW rules config
    def __config_dtag_to_stag(self):
        app.logger.info(f'initializing the dtag_to_stag config')
        dtag_to_stag = {}
        for rule in self.__fw_rules:
            dest_tag = rule["dest_tag"]
            if dest_tag in dtag_to_stag:
                dtag_to_stag[dest_tag].add(rule["source_tag"])
            else:
                dtag_to_stag[dest_tag] = {rule["source_tag"]}
        self.dtag_to_stag = dtag_to_stag
        app.logger.info(f'Configured dtag_to_stag: {dtag_to_stag}')

    # vm_id -> vm_ids
    # use tag_to_vms & dtag_to_stag
    def __config_vm_to_vms(self):
        app.logger.info(f'initializing the vm_to_vms config')
        vm_to_vms = {}
        for vm in self.__vms_cfg:
            vm_id = vm["vm_id"]
            vm_to_vms[vm_id] = set()
            source_tags = set()
            for tag in vm["tags"]:
                if tag in self.dtag_to_stag:
                    source_tags = source_tags.union(self.dtag_to_stag[tag])
            for source_tag in source_tags:
                if source_tag in self.tag_to_vms:
                    vm_to_vms[vm_id] = vm_to_vms[vm_id].union(self.tag_to_vms[source_tag])
        self.__vm_to_vms = vm_to_vms
        app.logger.info(f'Configured vm_to_vms: {vm_to_vms}')

    # get list of vms that can attack <vm>
    def vulnerable_to(self, vm_id):
        app.logger.info(f'Getting list of Virtual Machines that can potentially attack: {vm_id}')
        vm_list = self.__vm_to_vms[vm_id]
        if vm_list:
            app.logger.info(f'VM {vm_id} can be attacked by: {vm_list}')
        else:
            app.logger.info(f'VM {vm_id} is safe from potential attacks')
        return vm_list

    # def get_stats(self):
        # the_time = timeit.Timer('Cloud.vulnerable_to(Cloud.vm_ids[0])', 'from cloud import Cloud').timeit()
        # the_time = t.timeit(number=1)
        # app.logger.info(f'Avg time of request is: {the_time}')
        # return the_time
        # request count
        # vm count
