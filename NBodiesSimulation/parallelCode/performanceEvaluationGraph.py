#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GREEN is for single Raspberry Pi running regular single threaded code
# RED is for single Raspberry Pi running cluster framework
# BLUE is for two Raspberry Pis running cluster framework


import matplotlib.pyplot as plt
plt.plot([0,10,20,100,750,1000,1500,2000],[0,0.0553579330444,0.113780975342,1.63989710808,93.1174659729,157.974377155,350.750167847,653.90922904],'g',label="Regular single thread program")
plt.plot([0,10,20,100,750,1000,1500,2000], [0,0.325753927231,0.391202926636,1.83082985878,63.8195700645,116.336795807,256.967527866,445.415707827], 'r',label="Single RPi cluster")
plt.plot([0,10,20,100,750,1000,1500,2000], [0,0.483030080795,0.516968011856,1.35956478119,35.0477330685,60.0290260315,133.784164906,233.588376999], 'b',label="Dual RPi cluster")
plt.ylabel('Simulation Time (seconds)')
plt.xlabel('Number of Planets')

legend = plt.legend(loc='upper center', shadow=True)

plt.show()


# 1000 Planets on 1 node = 68.4913618565 seconds
# 1000 Planets on 2 nodes = 91.3218100071 seconds

# 2000 Planets on 1 node = 251.619503975 seconds
# 2000 Planets on 2 nodes = 325.611490965 seconds


#1000 planets with regular single threaded code = 154.161368132 seconds
#1000 planets with two Raspberry Pis running cluster framework = 58.9151871204 seconds
#1000 planets with 1 raspberry pi running cluster framework = 113.848109961 seconds
