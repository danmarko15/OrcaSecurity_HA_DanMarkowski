import json

from flask import current_app as app


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Cloud(metaclass=Singleton):
    def __init__(self, cloud_env_cfg=None):
        app.logger.info(f'initializing the cloud environment')
        if cloud_env_cfg:
            with open(cloud_env_cfg) as cloud_json_cfg:
                cloud_env = json.load(cloud_json_cfg)
                self.__vms_cfg = cloud_env["vms"]
                self.vm_count = len(self.__vms_cfg)
                self.__fw_rules = cloud_env["fw_rules"]
                self.__init_cloud_env()

    def __init_cloud_env(self):
        self.__config_tag_to_vmid()
        self.__config_dtag_to_stag()
        self.__config_vm_vulnerable_to_vms()

    def __config_tag_to_vmid(self):
        """Configure the tag to vm_ids using input VM config, mapping which VMs are tagged with 'tag'"""
        app.logger.info(f'initializing the tag_to_vmid config')
        tag_to_vmid = {}
        for vm in self.__vms_cfg:
            for tag in vm["tags"]:
                if tag in tag_to_vmid:
                    tag_to_vmid[tag].add(vm["vm_id"])
                else:
                    tag_to_vmid[tag] = {vm["vm_id"]}
        self.tag_to_vmid = tag_to_vmid
        app.logger.info(f'Configured tag_to_vmid: {tag_to_vmid}')

    def __config_dtag_to_stag(self):
        """Configure the dest_tag to src_tag using input FW rules config, mapping which tags can potentially be
        attacked by which other tags"""
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

    def __config_vm_vulnerable_to_vms(self):
        """Configure the vm_vulnerable_to_vms, mapping what VM can potentially be attacked by which VMs"""
        app.logger.info(f'initializing the vm_vulnerable_to_vms config')
        vm_vulnerable_to_vms = {}
        for vm in self.__vms_cfg:
            vm_id = vm["vm_id"]
            vm_vulnerable_to_vms[vm_id] = set()
            source_tags = set()
            for tag in vm["tags"]:
                if tag in self.dtag_to_stag:
                    source_tags = source_tags.union(self.dtag_to_stag[tag])
            for source_tag in source_tags:
                if source_tag in self.tag_to_vmid:
                    vm_vulnerable_to_vms[vm_id] = vm_vulnerable_to_vms[vm_id].union(self.tag_to_vmid[source_tag])
        self.__vm_to_vms = vm_vulnerable_to_vms
        app.logger.info(f'Configured vm_vulnerable_to_vms: {vm_vulnerable_to_vms}')

    # get list of vms that can attack <vm>
    def vulnerable_to(self, vm_id):
        """Return VM list that can potentially attack vm_id"""
        app.logger.info(f'Getting list of Virtual Machines that can potentially attack: {vm_id}')
        vm_list = self.__vm_to_vms[vm_id]
        if vm_list:
            app.logger.info(f'VM {vm_id} can be attacked by: {vm_list}')
        else:
            app.logger.info(f'VM {vm_id} is has no potential attackers')
        return vm_list
