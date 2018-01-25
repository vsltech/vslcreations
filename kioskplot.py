#KIOSK FILTERING CO-EFFICIENT RELATION FROM CSV & EXPORTING TO CSV
#CODED BY VISHAL ADITYA | EMBEDDED SOFTWARE ENGINEER | MIISKY TECHNOVATION PVT. LTD.

import math,csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('kioskdata.csv')
x = []
for data in df['50']:
	x.append(data)
y = [187,170,185,156,220,114,175,87,136,190,210,130,186,95,110,146,210,70,150,86,210,210,155,130,107,70,230,150,105,94,230,170,210,150,108,100,139,190,86,170,202,83,159,126,210,280,137,305,147,135,110,122,150,177,158,160,174,135,183,219,184,205,147,179,216,75,140,197,99,148,138,138,168,190,153,283,163,210,368,90,103,194,106,150,220,80,184,82,117,318,190,99,164,210,170,203,120,183,260,88]
plt.scatter(x, y, color = "m",marker = "o", s = 30)
plt.plot(x, y, color = "g",linewidth=0.5)
# putting labels
plt.xlabel('X: Device Readings')
plt.ylabel('Y: Lab Readings')
# function to show plot
plt.show()
