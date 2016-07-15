#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pylab as plt

ax = plt.subplot(111)
ax.set_title("Single Node Test Results")
ax.set_xlabel("# Slave processes")
ax.set_ylabel("# Time (seconds) to factor number")

slave_processes = [1,2,3,4,5,6]
time_taken = [38.3,20.5,19.4,19.3,19.5,19.2]


ax.bar(slave_processes, time_taken, width=0.2,color='bgry',align='center')
plt.show()
