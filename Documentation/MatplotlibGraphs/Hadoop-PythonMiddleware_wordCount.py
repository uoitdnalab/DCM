#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pylab as plt

ax = plt.subplot(111)
ax.set_title("Word Frequency analysis test")
ax.set_xlabel("# Slave processes")
ax.set_ylabel("# Time (seconds) to complete word count")

slave_processes = [1,2,3,4]
hadoop_slave_processes = [x-0.1 for x in slave_processes]
pyro_slave_processes = [x+0.1 for x in slave_processes]
hadoop_time_taken = [996.7,0,0,0] # replace zeros with actual values
#pyro_time_taken = [16.2,22.8,26.9,30.0]
pyro_time_taken = [32.7,47.2,0,0]


b1 = ax.bar(hadoop_slave_processes, hadoop_time_taken, width=0.2,color='b',align='center')
b2 = ax.bar(pyro_slave_processes, pyro_time_taken, width=0.2,color='r',align='center')

ax.legend([b1,b2],["Apache Hadoop","Middleware for Physical Computing"], loc = 'lower center')

plt.show()
