# OrcaSecurity_HA_DanMarkowski
Attack Surface Service handles a cloud environment and supports 2 APIs.

To start the service, simply run the following cmd from terminal:
python attacksurface/attack_surface.py --cloud input-path

The service accepts 1 argument '--cloud' that is the path to the input JSON data

Attack Surface will pre-process the cloud environment on startup and configure the data to minimize request process time.

The log file 'attack_surface.log' will be created in the root dir to trace service logs. 

APIs:
    
    /api/v1.0/attack
    Accepts one querty parameter 'vm_id' and returns all vm_ids that can potentially attack it

    /api/v1.0/stats
    Returns the service stats: 
        -Number of Virtual Machines in the cloud
        -Number of requests made to all endpoints
        -Average request processing time in milliseconds

 
