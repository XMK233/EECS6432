# -*- coding: utf-8 -*-
import json
import requests
import time
from urllib.request import urlopen
import math   # This will import math module
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
    with open("dataop-pi_data-gathering.txt", "w") as f:
        while True:
            print("======================web server: ==========================")
            f.write("======================web server: ==========================" + "\n")

            CtnNum = settings.get_tasks(services["web-worker"])
            print("Originally, this tier has %d containers" %(CtnNum))
            f.write("Originally, this tier has %d containers" %(CtnNum) + "\n")

            Uw_cpu = getMetrics.calculate_cpu_utilization(nodes, services["web-worker"])
            print("CPU Usage (avg): {0:.2f}%".format(Uw_cpu * 100))
            f.write("CPU Usage (avg): {0:.2f}%".format(Uw_cpu * 100) + "\n")

            Xw = getMetrics.calculate_data_incoming_rate(nodes, services["web-worker"])
            print("average data arrival rate: %f Kb/s\n" % (Xw))
            f.write("average data arrival rate: %f Kb/s\n" % (Xw) + "\n")
#-----------------------------------------------
            if Xw == float(0):
                mtp = 1
            else:
                mtp = abs(Xw*R_-Uw_cpu)/(Xw*R_*Uw_cpu)

            print("new number of containers should be %f x" %(mtp))
            f.write("new number of containers should be %f x" %(mtp) + "\n")

            NewCtnNum = round(CtnNum / math.sqrt(mtp))
            print("--> Given the utilization here, we want new number of containers in this tier to be (U/(1-U)/R_): ", NewCtnNum)
            f.write("--> Given the utilization here, we want new number of containers in this tier to be (U/(1-U)/R_): %d" %(NewCtnNum) + "\n")

            NewCtnNum = min(NewCtnNum, 15)

            if Uw_cpu > 0.6 and NewCtnNum > CtnNum:
                settings.scale(services["web-worker"], NewCtnNum, 1)
            elif Uw_cpu < 0.3 and NewCtnNum < CtnNum:
                if NewCtnNum>0:
                    settings.scale(services["web-worker"], NewCtnNum, -1)
                else:
                    settings.scale(services["web-worker"], 1, -1)

            '''print("database: ")
            print("CPU Usage (avg): {0:.2f}%".format(
                getMetrics.calculate_cpu_utilization(nodes, services["mysql"]) * 100))
            print("average data arrival rate: %f Kb/s\n" % (
                getMetrics.calculate_data_incoming_rate(nodes, services["mysql"])))'''
            print("================================================")
            f.write("================================================" + "\n")
            time.sleep(50)