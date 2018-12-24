# -*- coding: utf-8 -*-
import pandas as pd
import sys
sys.path.append("..")
import settings, getMetrics
import json, requests, time
from urllib.request import urlopen
import datetime
import math   # This will import math module
import matplotlib.pyplot as plt
import random

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
    time_limit = datetime.timedelta(seconds=3600)
    start_time = datetime.datetime.now()
    version_interval = datetime.timedelta(seconds=600)
    print("let's get started")

    with open("ML_dataop-pi_data-gathering_start--%s.csv" %(start_time.strftime("%Y-%m-%d_%H-%M-%S")), "w") as f:

        ctnnums = []
        uw_cpus = []
        xws = []
        mtps = []
        newctnnum = []
        actctnnum = []
        rs = []

        last_checkpoint = start_time
        f.write("CtnNum,Uw_cpu,Xw,mtp,NewCtnNum,ActNewCtnNum\n")

        f_version = open("ML_dataop-pi_data-gathering_version--%s.csv" %(start_time.strftime("%Y-%m-%d_%H-%M-%S")))
        f_version.write("CtnNum,Uw_cpu,Xw,mtp,NewCtnNum,ActNewCtnNum\n")

        while True:
            print("======================web server: ==========================")

            now_time = datetime.datetime.now()
            if now_time - start_time >= time_limit:
                f_version.close()
                break

            now = datetime.datetime.now()
            if now - last_checkpoint >= version_interval:
                last_checkpoint = now
                f_version.close()
                f_version.open(
                    "ML_dataop-pi_data-gathering_version--%s.csv" % (last_checkpoint.strftime("%Y-%m-%d_%H-%M-%S")))
                pass

            CtnNum = settings.get_tasks(services["web-worker"])
            print("Originally, this tier has %d containers" %(CtnNum))
            f.write(str(CtnNum) + ",")
            f_version.write(str(CtnNum) + ",")
            ctnnums.append(CtnNum)

            Uw_cpu = getMetrics.calculate_cpu_utilization(nodes, services["web-worker"])
            print("CPU Usage (avg): {0:.2f}%".format(Uw_cpu * 100))
            f.write(str(Uw_cpu) + ",")
            f_version.write(str(Uw_cpu) + ",")
            uw_cpus.append(Uw_cpu)

            Xw = getMetrics.calculate_data_incoming_rate(nodes, services["web-worker"])
            print("average data arrival rate: %f Kb/s\n" % (Xw))
            f.write(str(Xw) + "\n")
            f_version.write(str(Xw) + "\n")
            xws.append(Xw)

            rs.append(Uw_cpu / (Xw * (1 - Uw_cpu)) if Xw != 0 else 0)

            du = uw_cpus[-1] - uw_cpus[-2] if len(uw_cpus) > 1 else 0
            dx = xws[-1] - xws[-2] if len(xws) > 1 else 0
            dr = rs[-1] - R_

#-----------------------------------------------

            '''NewCtnNum = round(CtnNum / math.sqrt(mtp))#
            print("--> Given the utilization here, we want new number of containers in this tier to be: ", NewCtnNum)
            f.write(str(NewCtnNum) + ",")
            newctnnum.append(NewCtnNum)

            ActNewCtnNum = min(NewCtnNum, 15)
            print("--> but actually, we scale the number of containers to be ", ActNewCtnNum)
            f.write(str(ActNewCtnNum) + "\n")
            actctnnum.append(ActNewCtnNum)'''

            request_data = {"instances": [[du, dx, dr]]}
            url = "http://scale05.eecs.yorku.ca:8502/v1/models/ctnnum_model:predict"
            r = requests.post(url, json=request_data)
            NewCtnNum = math.ceil(json.loads(r.text)["predictions"][0][0])
            ActNewCtnNum = 1 if CtnNum + NewCtnNum <= 0 else CtnNum + NewCtnNum
            ActNewCtnNum = min(ActNewCtnNum, 5)

            print(request_data, ActNewCtnNum)

            if Uw_cpu > 0.15 and ActNewCtnNum > CtnNum:
                settings.scale(services["web-worker"], ActNewCtnNum, 1)
            elif Uw_cpu < 0.1 and ActNewCtnNum < CtnNum:
                if ActNewCtnNum>0:
                    settings.scale(services["web-worker"], ActNewCtnNum, -1)
                else:
                    settings.scale(services["web-worker"], 1, -1)
#-----------------------------------------------------------------------------------
            fig, ax1 = plt.subplots()
            t = range(len(ctnnums))
            ax1.set_xlabel('#sample (s)')
            ###
            ax1.plot(t, ctnnums, 'b-')
            ax1.set_ylabel('#ctn', color='b')
            ax1.tick_params('y', colors='b')
            ###
            ax2 = ax1.twinx()
            ax2.plot(t, uw_cpus, 'r-')
            ax2.set_ylabel('Uw_cpu', color='r')
            ax2.tick_params('y', colors='r')
            ###
            ax3 = ax1.twinx()
            ax3.plot(t, xws, 'g-')
            ax3.set_ylabel('Xw', color='g')
            ax3.tick_params('y', colors='g')
            ###
            plt.savefig("images_%s.png" %(start_time.strftime("%Y-%m-%d_%H-%M-%S")))
            plt.close()
#______________________________________________________________________________________
            time.sleep(2)