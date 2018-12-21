import json
import requests
import time
from urllib.request import urlopen

# here we assume you tunneled port 4000 of all swarm nodes to ports on your local machine
nodes_list = ["192.168.56.103:4000", "192.168.56.104:4000", "192.168.56.105:4000"]

# the address your managers nodes REST API is listening
manager = nodes_list[2]

# upper and lower cpu usage thresholds where scaling should happen on
cpu_upper_threshold = 0.5
cpu_lower_threshold = 0.2

# time interval between each avg cpu usage calculations
interval = 5

target_response_time = 0.02

def scale(service, replicas, direction = 0):
    if direction == 0:
        pass
    elif direction == 1:
        print("scaling up to %d"%(replicas))
    else:
        print("scale down to %d"%(replicas))

    # get the service - we need the version of the service object
    with urlopen("http://{manager}/services/{service}".format(manager=manager, service=service["name"]),) as url:    # just an "s", would that make difference?
        data = json.loads(url.read().decode())
        version = data["Version"]["Index"]

        # the whole spec object should be sent to the update API,
        # otherwise the missing values will be replaced by default values
        spec = data["Spec"]
        spec["Mode"]["Replicated"]["Replicas"] = replicas

        r = requests.post("http://{manager}/services/{service}/update?version={version}".format(manager=manager,    # just an "s", would that make difference?
                                                                                                service=service["name"],
                                                                                                version=version),
                          data=json.dumps(spec))
        if r.status_code == 200:
            print("scale completed. ")
            get_tasks(service)
        else:
            print(r.reason, r.text)

    return

# get_tasks functions gets a service in the form of {"name": <service-name>, "tasks": []} and fills the tasks.
def get_tasks(service):
    service["tasks"] = []
    with urlopen(
            'http://{manager}/tasks?filters={{"service":{{"{service}":true}},"desired-state":{{"running":true}}}}'.format(
                manager=manager, service=service["name"])) as url:
        data = json.loads(url.read().decode())
        print("{service} tasks:".format(service=service["name"]))
        for task in data:
            if task["Status"]["State"] == "running":
                container_id = task["Status"]["ContainerStatus"]["ContainerID"]
            else:
                continue
            node_id = task["NodeID"]
            service["tasks"].append({"ContainerID": container_id, "NodeID": node_id})
            print('''\t ContainerID: {}, NodeID: {} '''.format(container_id, node_id))
        return len(data)