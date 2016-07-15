#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pylab as plt

ax = plt.subplot(111)
ax.set_title("Factoring 425,432,980")
ax.set_xlabel("# Raspberry Pi nodes")
ax.set_ylabel("# Time (seconds) to factor number")

slave_processes = [1,2,3,4]
time_taken = [386.0,191.9,128.3,99.0]


ax.bar(slave_processes, time_taken, width=0.2,color='bgry',align='center')
plt.show()
