#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cluster
import time
import json
import sys

beginTime = time.time()

#Size of the cluster
WORKER_NODES = 1

# The gravitational constant G
G = 6.67428e-11

planetFileName = sys.argv[1]

planets = [] #List of planets in the simulation

""" Performs a simple merge of two dictionarys """
def simple_merge(pd1,pd2):
	merge_result = {}
	for key in pd1:
		merge_result[key] = pd1[key]
	
	for key in pd2:
		merge_result[key] = pd2[key]
	
	return merge_result

cluster.network_init('eth0','192.168.137.100',99)
cluster.round_robin_init(WORKER_NODES)

#Make sure all slave nodes are reset
reset_procs = cluster.broadcast_task("reset_slave")
cluster.wait_for_broadcast_task(reset_procs)

emp_nodes = [] #employed nodes


#Distribute force calculating tasks with information from the planets.json file
for node_index in range(0,WORKER_NODES):
	emp_nodes.append(cluster.concurrent_task_file('calculate_planets_json','t_' + str(node_index),planetFileName,planetFileName,node_index,WORKER_NODES))

outputs = [] #the outputs from each slave task --- a subset of the planets which have been calculated as to how they interact with the complete set.

#Wait for these tasks to finish --- and get outputs
for node_index in range(0,len(emp_nodes)):
	cluster.wait_for_task('t_'+str(node_index),emp_nodes[node_index])
	outputs.append(cluster.get_output_from_task('t_'+str(node_index),emp_nodes[node_index]))

#Merge all outputs
while len(outputs) > 1:
	planets1 = outputs.pop()
	planets2 = outputs.pop()
	outputs.append(simple_merge(planets1,planets2))

#Clear the console
for i in range(0,5):
	print ""


print "========= COMPLETED SIMULATION ========="

#print outputs

for planet_id in outputs[0]:
	print planet_id + " ---> " + str(outputs[0][planet_id]["fnet_x"]) + " , " + str(outputs[0][planet_id]["fnet_y"])

elapsedTime = time.time() - beginTime

print " #### ELAPSED TIME: " + str(elapsedTime) + " seconds"



