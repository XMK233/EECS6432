# -*- coding: utf-8 -*-
import json
import requests
import time
from urllib.request import urlopen
import math   # This will import math module
import system.settings, system.getMetrics

if __name__ == '__main__':
    # get all NodeIDs in swarm
    nodes = {}
    print("Nodes:")
    for node in system.settings.nodes_list:
        with urlopen("http://{node}/info".format(node=node)) as url:
            data = json.loads(url.read().decode())
            nodes[data["Swarm"]["NodeID"]] = node
            print('''\t NodeID: {} '''.format(
                data["Swarm"]["NodeID"], ))

    # list all the services
    services = {}
    with urlopen("http://{manager}/services".format(manager=system.settings.manager)) as url:
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
        system.settings.get_tasks(service)

    # cpu usage api is not fast. be patient!
    # here we consistently get the cpu usage of all the web-workers and calculate the average

    R_ = system.settings.target_response_time
    with open("dataop-pi_data-gathering.txt", "w") as f:
        while True:
            print("======================web server: ==========================")
            f.write("======================web server: ==========================")

            CtnNum = system.settings.get_tasks(services["web-worker"])
            print("Originally, this tier has %d containers" %(CtnNum))
            f.write("Originally, this tier has %d containers" %(CtnNum))

            Uw_cpu = system.getMetrics.calculate_cpu_utilization(nodes, services["web-worker"])
            print("CPU Usage (avg): {0:.2f}%".format(Uw_cpu * 100))
            f.write("CPU Usage (avg): {0:.2f}%".format(Uw_cpu * 100))

            NewCtnNum = round(CtnNum * math.pow(2, 2*(Uw_cpu/0.5-1)))
            print("--> Given the utilization here, we want new number of containers in this tier to be round(CtnNum * math.pow(2, 2*Uw_cpu/0.5-1)): ", NewCtnNum)
            f.write("--> Given the utilization here, we want new number of containers in this tier to be round(CtnNum * math.pow(2, 2*Uw_cpu/0.5-1)): %d" %(NewCtnNum))

            NewCtnNum = min(NewCtnNum, 15)

            if Uw_cpu > 0.6 and NewCtnNum > CtnNum:
                system.settings.scale(services["web-worker"], NewCtnNum, 1)
            elif Uw_cpu < 0.4 and NewCtnNum < CtnNum:
                if NewCtnNum>0:
                    system.settings.scale(services["web-worker"], NewCtnNum, -1)
                else:
                    system.settings.scale(services["web-worker"], 1, -1)


            '''print("database: ")
            print("CPU Usage (avg): {0:.2f}%".format(
                getMetrics.calculate_cpu_utilization(nodes, services["mysql"]) * 100))
            print("average data arrival rate: %f Kb/s\n" % (
                getMetrics.calculate_data_incoming_rate(nodes, services["mysql"])))'''
            print("================================================")
            f.write("================================================")
            time.sleep(50)