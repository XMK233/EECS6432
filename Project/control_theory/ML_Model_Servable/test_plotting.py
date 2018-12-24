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

df = pd.read_csv(r"C:\Users\xmk233\PycharmProjects\EECS6432\Project\control_theory\ML_Model_Servable\ML_dataop-pi_data-gathering_2018-12-23_18-52-52.csv")

fig, ax1 = plt.subplots()
t = range(len(df))
ax1.set_xlabel('#sample (s)')
###
ax1.plot(t, df["CtnNum"], 'b-')
ax1.set_ylabel('#ctn', color='b')
ax1.tick_params('y', colors='b')
###
ax2 = ax1.twinx()
ax2.plot(t, df["Uw_cpu"] * 3, 'r-')
ax2.set_ylabel('Uw_cpu', color='r')
ax2.tick_params('y', colors='r')
###
ax3 = ax1.twinx()
ax3.plot(t, df["Xw"], 'g-')
ax3.set_ylabel('Xw', color='g')
ax3.tick_params('y', colors='g')
###
#plt.savefig("images_pretty.png")
plt.show()
plt.close()