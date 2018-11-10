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
    '''print("scaling triggered...")'''

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
            print("after scaling: ")
            get_tasks(service, 2)
        else:
            print(r.reason, r.text)

    return

# https://en.wikipedia.org/wiki/Proportional_control
# e(t) = SP - PV
def e(sp, pv):
    return sp - pv

################################################################
#### class definition  ####################

class PID:
    proportional_gain = 0
    integral_gain = 0
    derivative_gain = 0
    scale_bound = 15

    def __init__(self, p = 1, i = 0, d = 0, sb = 15):
        self.proportional_gain = p
        self.integral_gain = i
        self.derivative_gain = d
        self.scale_bound = sb

        return

    def output(self, interval, set_point, current_value, last_value, history_values):
        # PID Controller

        # Proportional gain - e(t)
        output_proportional_controller = self.proportional_gain * e(set_point, current_value)
        print("Output Proportional Controller: {0}".format(output_proportional_controller))

        # Integral gain (using last five cpu usages) -> Sum
        output_integral_controller = self.integral_gain * (sum(history_values[-interval:]) * interval)
        print("Output Integral Controller: {0}".format(output_integral_controller))

        # Derivative gain: (e(k)-e(k-1))/T
        output_derivative_controller = self.derivative_gain * (
                e(set_point, current_value) - e(set_point, last_value) / interval)
        print("Output Derivative Controller: {0}".format(output_derivative_controller))

        controller_output = abs(
            round(output_proportional_controller + output_integral_controller + output_derivative_controller))

        print("Controller final output: {0}".format(controller_output))

        if controller_output > 0 and controller_output <= self.scale_bound:
            scale_num = controller_output
        elif controller_output > self.scale_bound:
            scale_num = self.scale_bound
        else:
            scale_num = 1

        return scale_num


class CPU_Controller:
    #definition
    cpu_lower_threshold = 0
    cpu_upper_threshold = 0
    services = None
    service_name = None

    def __init__(self, servs, serv_name, lower, upper):
        self.cpu_lower_threshold = lower
        self.cpu_upper_threshold = upper
        self.services = servs
        self.service_name = serv_name
        return

    def calculate_cpu_percent(self, d):
        cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
        cpu_proportino = 0.0
        cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                    float(d["precpu_stats"]["cpu_usage"]["total_usage"])
        system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - \
                       float(d["precpu_stats"]["system_cpu_usage"])
        if system_delta > 0.0:
            cpu_proportino = cpu_delta / system_delta * cpu_count # * 100.0
        return cpu_proportino

    def control(self, pid, interval):
        # running value(s)
        cpu_usage_avg_prev = None
        cpu_usage_avg_arr = []

        set_point = (self.cpu_upper_threshold + self.cpu_lower_threshold) / 2

        #plt.ion()

        while True:

            cpu_usages = []

            # set which service you want to analyze.
            service_in_analysis_name = self.service_name
            print("-----------------------new round-----------------")
            get_tasks(self.services[service_in_analysis_name])

            for task in self.services[service_in_analysis_name]["tasks"]:
                url_ = 'http://{node}/containers/{containerID}/stats?stream=false'.format(node=nodes[task["NodeID"]],
                                                                                          containerID=task[
                                                                                              "ContainerID"])
                with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                        node=nodes[task["NodeID"]],
                        containerID=task["ContainerID"])) as url:  # , context=nodes[task["NodeID"]][1]
                    data = json.loads(url.read().decode())
                    cpu_usages.append(self.calculate_cpu_percent(data))

            cpu_usage_avg = sum(cpu_usages) / len(cpu_usages)
            cpu_usage_avg_arr.append(cpu_usage_avg)

            if cpu_usage_avg_prev == None:
                cpu_usage_avg_prev = cpu_usage_avg

            print("Previous CPU Usage (avg): {0:.2f}%".format(cpu_usage_avg_prev * 100) )#
            print("CPU Usage (avg): {0:.2f}%".format(cpu_usage_avg * 100))#
            print("CPU Setpoints are currently from {low:.2f}% to {high:.2f}%".format(low=self.cpu_lower_threshold * 100,
                                                                                      high=self.cpu_upper_threshold * 100))

            scale_num = pid.output(interval, set_point, cpu_usage_avg, cpu_usage_avg_prev, cpu_usage_avg_arr)
            '''print("Scale parameter value: ", scale_num)'''

            #print("-------------")

            cpu_usage_avg_prev = cpu_usage_avg

            get_tasks(self.services[service_in_analysis_name])
            task_count = len(self.services[service_in_analysis_name]["tasks"])

            if cpu_usage_avg > self.cpu_upper_threshold:
                # scale up
                scale(self.services[service_in_analysis_name], task_count + scale_num, direction=1)

            elif cpu_usage_avg < self.cpu_lower_threshold:
                # scale down
                if task_count > 1:
                    scale(self.services[service_in_analysis_name], task_count - scale_num, direction=-1)
            else:  # do nothing
                pass

            # block the main thread for <interval> seconds
            x = range(len(cpu_usage_avg_arr))
            plt.hlines(set_point, x[0], len(cpu_usage_avg_arr))
            plt.plot(x, cpu_usage_avg_arr)
            plt.savefig("images.png")
            time.sleep(interval)



############################################################################################################
#####   Operating Zone   #######################


# here we assume you tunneled port 4000 of all swarm nodes to ports on your local machine
nodes_list = ["192.168.56.103:4000", "192.168.56.104:4000", "192.168.56.101:4000"]

# the address your managers nodes REST API is listening
manager = "192.168.56.101:4000"

# upper and lower cpu usage thresholds where scaling should happen on
'''cpu_upper_threshold = int(input("Enter a number from 0 to 100 for the CPU upper threshold: ")) / 100 # 0.50
cpu_lower_threshold = int(input("Enter a number from 0 to 100 for the CPU lower threshold: ")) / 100 # 0.10'''

# p, i, d parameters to be tested
'''proportional_gain = int(input("Enter a number for Kp: "))
integral_gain = int(input("Enter a number for Ki: "))
derivative_gain = int(input("Enter a number for Kd: "))'''

# time interval between each avg cpu usage calculations
'''interval = int(input("Enter a number for the interval: "))'''
time_interval = 5

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
''''''
cpu0 = CPU_Controller(services, "web-worker", 0.1, 0.5)
pid_for_cpu0 = PID(1, 1, 1, 15)
cpu0.control(pid_for_cpu0, time_interval)

# force scaling
scale(services["web-worker"], 3, -1)
