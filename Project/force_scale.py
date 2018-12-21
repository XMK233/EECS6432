import json
import requests
import time
from urllib.request import urlopen
import matplotlib.pyplot as plt
import urllib
import socket
import ssl
import urllib3

def get_tasks(service, verbose = 0):
    service["tasks"] = []

    with urlopen(
            'http://{manager}/tasks?filters={{"service":{{"{service}":true}},"desired-state":{{"running":true}}}}'.format(
                manager=manager, service=service["name"])) as url:
        data = json.loads(url.read().decode())
        '''print("{service} tasks:".format(service=service["name"]))'''
        for task in data:
            if task["Status"]["State"] == "running":
                container_id = task["Status"]["ContainerStatus"]["ContainerID"]
            else:
                continue
            node_id = task["NodeID"]
            service["tasks"].append({"ContainerID": container_id, "NodeID": node_id})
            #'''print('''\t ContainerID: {}, NodeID: {} '''.format(container_id, node_id))'''

        if verbose == 1:
            print("{service} tasks:".format(service=service["name"]))
            for c in service["tasks"]:
                print('''\t ContainerID: {}, NodeID: {} '''.format(c["ContainerID"], c["NodeID"]))
        elif verbose == 2:
            print("Number of tasks in service %s: %d" %(service["name"], len(service["tasks"])))

    return

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

############################################################################################################
#####   Operating Zone   #######################


# here we assume you tunneled port 4000 of all swarm nodes to ports on your local machine
nodes_list = ["192.168.56.103:4000", "192.168.56.104:4000", "192.168.56.105:4000"]

# the address your managers nodes REST API is listening
manager = "192.168.56.105:4000"

time_interval = 1

# get all NodeIDs in swarm
nodes = {}
print("Nodes:")
for node in nodes_list:
    with urlopen("http://{node}/info".format(node=node)) as url:
        data = json.loads(url.read().decode())
        nodes[data["Swarm"]["NodeID"]] = node
        print('''\t NodeID: {} '''.format(
            data["Swarm"]["NodeID"], ))

# list all the services
services = {}
with urlopen("http://{manager}/services".format(manager=manager)) as url:
    data = json.loads(url.read().decode())
    print("Services:")
    for service in data:
        services[service["Spec"]["Name"]] = {"name": service["Spec"]["Name"], "tasks": []}
        print('''\t name: {}, version: {}, replicas: {}  '''.format(
            service["Spec"]["Name"],
            service["Version"]["Index"],
            service["Spec"]["Mode"]["Replicated"]["Replicas"]))

# get the tasks running on our swarm cluster
for service_name, service in services.items():
    get_tasks(service, 1)

# force scaling
scale(services["web-worker"], 1, 1)
