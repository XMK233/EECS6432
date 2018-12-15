import json
import requests
import time
from urllib.request import urlopen
import settings, getMetrics

if __name__ == '__main__':
    # get all NodeIDs in swarm
    nodes = {}
    print("Nodes:")
    for node in settings.nodes_list:
        with urlopen("http://{node}/info".format(node=node)) as url:
            data = json.loads(url.read().decode())
            nodes[data["Swarm"]["NodeID"]] = node
            print('''\t NodeID: {} '''.format(
                data["Swarm"]["NodeID"], ))

    # list all the services
    services = {}
    with urlopen("http://{manager}/services".format(manager=settings.manager)) as url:
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
        settings.get_tasks(service)

    # cpu usage api is not fast. be patient!
    # here we consistently get the cpu usage of all the web-workers and calculate the average

    while True:
        print("web server: ")
        print("CPU Usage (avg): {0:.2f}%".format(getMetrics.calculate_cpu_utilization(nodes, services["web-worker"]) * 100))
        print("average data arrival rate: %f Kb/s\n" % (getMetrics.calculate_data_incoming_rate(nodes, services["web-worker"])))
        print("database: ")
        print("CPU Usage (avg): {0:.2f}%".format(
            getMetrics.calculate_cpu_utilization(nodes, services["mysql"]) * 100))
        print("average data arrival rate: %f Kb/s\n" % (
            getMetrics.calculate_data_incoming_rate(nodes, services["mysql"])))
        time.sleep(5)