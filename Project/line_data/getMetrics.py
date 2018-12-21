import json
import datetime, time
from urllib.request import urlopen

def calculate_cpu_utilization(nodes, service):
    cpu_usages = []
    for task in service["tasks"]:
        with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]], containerID=task["ContainerID"])) as url:
            data = json.loads(url.read().decode())

            cpu_count = len(data["cpu_stats"]["cpu_usage"]["percpu_usage"])
            cpu_percent = 0.0
            cpu_delta = float(data["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                        float(data["precpu_stats"]["cpu_usage"]["total_usage"])
            system_delta = float(data["cpu_stats"]["system_cpu_usage"]) - \
                           float(data["precpu_stats"]["system_cpu_usage"])
            if system_delta > 0.0:
                cpu_percent = cpu_delta / system_delta * cpu_count  # * 100.0

            cpu_usages.append(cpu_percent)

    cpu_usage_avg = sum(cpu_usages) / len(cpu_usages)
    return cpu_usage_avg

def calculate_data_incoming_rate(nodes, service):
    ars = []
    for task in service["tasks"]:

        t1 = datetime.datetime.now()
        d1 = 0
        with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]], containerID=task["ContainerID"])) as url:
            data = json.loads(url.read().decode())

            #d1 = data["networks"]["eth0"]["rx_bytes"] + data["networks"]["eth1"]["rx_bytes"] + data["networks"]["eth2"]["rx_bytes"]
            for key, value in data["networks"].items():
                d1 += value["rx_bytes"]

        time.sleep(1)

        t2 = datetime.datetime.now()
        d2 = 0
        with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]], containerID=task["ContainerID"])) as url:
            data = json.loads(url.read().decode())
            #d2 = data["networks"]["eth0"]["rx_bytes"] + data["networks"]["eth1"]["rx_bytes"] + data["networks"]["eth2"]["rx_bytes"]
            for key, value in data["networks"].items():
                d2 += value["rx_bytes"]

        ar = (d2 - d1)/float((t2-t1).total_seconds())
        ars.append(ar)
    return sum(ars)/ float(len(ars)) / 1024

def calculate_data_output_rate(nodes, service):
    ars = []
    for task in service["tasks"]:

        t1 = datetime.datetime.now()
        d1 = 0
        with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]], containerID=task["ContainerID"])) as url:
            data = json.loads(url.read().decode())

            for key, value in data["networks"].items():
                d1 += value["tx_bytes"]

        t2 = datetime.datetime.now()
        d2 = 0
        with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]], containerID=task["ContainerID"])) as url:
            data = json.loads(url.read().decode())

            for key, value in data["networks"].items():
                d2 += value["tx_bytes"]

        ar = (d2 - d1)/float((t2-t1).total_seconds())
        ars.append(ar)
    return sum(ars)/ float(len(ars)) / 1024

def calculate_data_io_rate(nodes, service):
    rxs = []
    txs = []
    for task in service["tasks"]:

        t1 = datetime.datetime.now()
        drx1 = 0
        dtx1 = 0
        with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]], containerID=task["ContainerID"])) as url:
            data = json.loads(url.read().decode())

            #d1 = data["networks"]["eth0"]["rx_bytes"] + data["networks"]["eth1"]["rx_bytes"] + data["networks"]["eth2"]["rx_bytes"]
            for key, value in data["networks"].items():
                drx1 += value["rx_bytes"]
                dtx1 += value["tx_bytes"]

        time.sleep(1)

        t2 = datetime.datetime.now()
        drx2 = 0
        dtx2 = 0
        with urlopen('http://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]], containerID=task["ContainerID"])) as url:
            data = json.loads(url.read().decode())
            #d2 = data["networks"]["eth0"]["rx_bytes"] + data["networks"]["eth1"]["rx_bytes"] + data["networks"]["eth2"]["rx_bytes"]
            for key, value in data["networks"].items():
                drx2 += value["rx_bytes"]
                dtx2 += value["tx_bytes"]

        rx = (drx2 - drx1)/float((t2-t1).total_seconds())
        tx = (dtx2 - dtx1)/float((t2-t1).total_seconds())
        rxs.append(rx)
        txs.append(tx)
    return {sum(rxs)/ float(len(rxs)) / 1024, sum(txs)/ float(len(txs)) / 1024}