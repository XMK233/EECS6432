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

    while True:
        print("======================mysql server: ==========================")

        CtnNum = settings.get_tasks(services["mysql"])
        print("Originally, this tier has %d containers" %(CtnNum))

        Uw_cpu = getMetrics.calculate_cpu_utilization(nodes, services["mysql"])
        print("CPU Usage (avg): {0:.2f}%".format(Uw_cpu * 100))

        Xw = getMetrics.calculate_data_incoming_rate(nodes, services["mysql"])
        print("average data arrival rate: %f Kb/s\n" % (Xw))
#-----------------------------------------------
        if Xw == float(0):
            mtp = 1
        else:
            mtp = (Xw*R_-Uw_cpu)/(Xw*R_*Uw_cpu)

        print(R_)
        print("new number of containers should be %f x" %(mtp))
        NewCtnNum = math.ceil(CtnNum / mtp)
        print("--> Given the utilization here, we want new number of containers in this tier to be (U/(1-U)/R_): ", NewCtnNum)

        '''NewCtnNum = (Xw * R_ - Uw_cpu) / (Xw * R_ * Uw_cpu) * CtnNum
        NewCtnNum = int(NewCtnNum) + 1
        print(NewCtnNum)'''

        NewCtnNum = min(NewCtnNum, 15)
        if NewCtnNum > CtnNum:
            settings.scale(services["mysql"], NewCtnNum, 1)
        elif NewCtnNum < CtnNum:
            if NewCtnNum>0:
                settings.scale(services["mysql"], NewCtnNum, -1)
            else:
                settings.scale(services["mysql"], 1, -1)


        '''print("database: ")
        print("CPU Usage (avg): {0:.2f}%".format(
            getMetrics.calculate_cpu_utilization(nodes, services["mysql"]) * 100))
        print("average data arrival rate: %f Kb/s\n" % (
            getMetrics.calculate_data_incoming_rate(nodes, services["mysql"])))'''
        time.sleep(5)