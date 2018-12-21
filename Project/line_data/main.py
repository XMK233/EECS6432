# -*- coding: utf-8 -*-
import json
import requests
import time
from urllib.request import urlopen
import datetime
import math   # This will import math module
import settings, getMetrics
import matplotlib.pyplot as plt

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
    time_limit = datetime.timedelta(seconds=3000)
    start_time = datetime.datetime.now()
    print("let's get started")

    with open("dataop-pi_data-gathering_%s.csv" %(start_time.strftime("%Y-%m-%d_%H-%M-%S")), "w") as f:

        ctnnums = []
        uw_cpus = []
        xws = []
        mtps = []
        newctnnum = []
        actctnnum = []

        f.write("CtnNum,Uw_cpu,Xw,mtp,NewCtnNum,ActNewCtnNum\n")

        while True:
            print("======================web server: ==========================")

            now_time = datetime.datetime.now()
            if now_time - start_time >= time_limit:
                break

            CtnNum = settings.get_tasks(services["web-worker"])
            print("Originally, this tier has %d containers" %(CtnNum))
            f.write(str(CtnNum) + ",")
            ctnnums.append(CtnNum)

            Uw_cpu = getMetrics.calculate_cpu_utilization(nodes, services["web-worker"])
            print("CPU Usage (avg): {0:.2f}%".format(Uw_cpu * 100))
            f.write(str(Uw_cpu) + ",")
            uw_cpus.append(Uw_cpu)

            Xw = getMetrics.calculate_data_incoming_rate(nodes, services["web-worker"])
            print("average data arrival rate: %f Kb/s\n" % (Xw))
            f.write(str(Xw) + ",")
            xws.append(Xw)
#-----------------------------------------------
            if Xw == float(0):
                mtp = 1
            else:
                mtp = abs(Xw*R_-Uw_cpu)/(Xw*R_*Uw_cpu)
            print("new number of containers should be %f x." %(mtp))
            f.write(str(mtp) + ",")
            mtps.append(mtp)

            NewCtnNum = round(CtnNum * mtp )#/ math.sqrt(mtp)
            print("--> Given the utilization here, we want new number of containers in this tier to be: ", NewCtnNum)
            f.write(str(NewCtnNum) + ",")
            newctnnum.append(NewCtnNum)

            ActNewCtnNum = min(NewCtnNum, 15)
            print("--> but actually, we scale the number of containers to be ", ActNewCtnNum)
            f.write(str(ActNewCtnNum) + "\n")
            actctnnum.append(ActNewCtnNum)

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