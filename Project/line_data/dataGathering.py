# -*- coding: utf-8 -*-
import json
import requests
import time, datetime
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

    R_ = settings.target_response_time

    start_time = datetime.datetime.now()
    time_limit = datetime.timedelta(seconds=4300)
    print("let's get started")
    with open("dataop-pi_data-gathering_%s.csv" %(start_time.strftime("%Y-%m-%d_%H-%M-%S")), "w") as f:
        while True:

            now_time = datetime.datetime.now()
            if now_time - start_time >= time_limit:
                break

            Uw_cpu = getMetrics.calculate_cpu_utilization(nodes, services["web-worker"])
            Xw = getMetrics.calculate_data_incoming_rate(nodes, services["web-worker"])
            data = [now_time.strftime("%Y-%m-%d %H:%M:%S"), str(Uw_cpu), str(Xw)]
            hehe = ",".join(data)
            print(hehe)
            f.write(hehe + "\n")

            '''Um_cpu = getMetrics.calculate_cpu_utilization(nodes, services["mysql"])
            Xm = getMetrics.calculate_data_incoming_rate(nodes, services["mysql"])
            data = [now_time.strftime("%Y-%m-%d %H:%M:%S"), str(Um_cpu), str(Xm)]
            hehe = ",".join(data)
            print(hehe)
            f.write(hehe + "\n")'''

            time.sleep(5)