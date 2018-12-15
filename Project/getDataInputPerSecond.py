import json
import requests
import time, datetime
from urllib.request import urlopen

# here we assume you tunneled port 4000 of all swarm nodes to ports on your local machine
nodes_list = ["192.168.56.101:4000", "192.168.56.103:4000", "192.168.56.104:4000"]

# the address your managers nodes REST API is listening
manager = "192.168.56.101:4000"

# upper and lower cpu usage thresholds where scaling should happen on
cpu_upper_threshold = 0.5
cpu_lower_threshold = 0.2

# time interval between each avg cpu usage calculations
interval = 5

def calculate_data_incoming_rate(service):
    ars = []
    for task in service["tasks"]:

        t1 = datetime.datetime.now()
        d1 = 0
        with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]], containerID=task["ContainerID"])) as url:
            data = json.loads(url.read().decode())

            d1 = data["networks"]["eth0"]["rx_bytes"] + data["networks"]["eth1"]["rx_bytes"] + data["networks"]["eth2"]["rx_bytes"]

        t2 = datetime.datetime.now()
        d2 = 0
        with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]], containerID=task["ContainerID"])) as url:
            data = json.loads(url.read().decode())
            d2 = data["networks"]["eth0"]["rx_bytes"] + data["networks"]["eth1"]["rx_bytes"] + data["networks"]["eth2"][
                "rx_bytes"]

        ar = (d2 - d1)/(t2 - t1)
        ars.append(ar)
    return sum(ars)/ float(len(ars))

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

# get all NodeIDs in swarm
if __name__ == '__main__':
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
        get_tasks(service)

    while True:
        t = calculate_data_incoming_rate(services["web-worker"])
        print(t)
        time.sleep(2)