#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pylab as plt

ax = plt.subplot(111)
ax.set_title("Single Raspberry Pi Test Results")
ax.set_xlabel("# Slave processes")
ax.set_ylabel("# Time (seconds) to factor number")

slave_processes = [1,2,3,4]
time_taken = [381.7,381.8,398.4,413.6]


ax.bar(slave_processes, time_taken, width=0.2,color='bgry',align='center')
plt.show()
