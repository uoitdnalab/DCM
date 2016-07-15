Integer Factorization
*********************

.. toctree::
   :maxdepth: 2


Single Laptop
###########

Specifications:
---------------

:OS: Debian Wheezy 7.5 64-bit, GNOME, Linux Kernel 3.2.0-4-amd64
:PC Model: HP Compaq tc4400
:Memory: 2.0GB
:Processor: Intel Core 2 CPU T7200 @ 2.00GHz x 2
:Python Version: 2.7.3

Test:
-----

The time was recorded for how long it would take to find all the
non-trivial factors of 425,432,980.

Results:
--------

The time to compute the factorization was 38 seconds with one process.
Once additional processes were added the computation time stayed
relatively constant at around 19 seconds.

.. figure:: singleNode.png

Single Raspberry Pi
####################

Specifications:
---------------
:OS: Raspbian Wheezy (2014-06-20)
:Installed Packages (Raspbian): python-pip, python2.7-dev
:Installed Packages (Python): Pyro4, netifaces
:Hardware: Raspberry Pi Model B


Test:
-----

The time was recorded for how long it would take to find all the
non-trivial factors of 425,432,980.

Results:
--------

The time to compute the factorization stayed at approximately 390
seconds regardless of how many processes were solving the problem.

.. figure:: singlePiNode.png

Raspberry Pi Cluster
####################

Specifications:
---------------
:OS: Raspbian Wheezy (2014-06-20)
:Installed Packages (Raspbian): python-pip, python2.7-dev
:Installed Packages (Python): Pyro4, netifaces
:Hardware: Raspberry Pi Model B


Test:
-----

The time was recorded for how long it would take to find all the
non-trivial factors of 425,432,980.

Results:
--------

The time to solve the problem could be estimated by the formula
:math:`t = 386/n` where :math:`t` is the time, in seconds, to solve
the problem and :math:`n` is the number of Raspberry Pi nodes working to
solve the problem.

.. figure:: multiPiNode.png

Source Code
###########

slave_program.py ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	
	import cluster
	import sys
	
	from cluster_slave_headers import *
	
	
	# Define how the slave program should set it's self up
	def slave_init(net_iface, ns_ip, node_id):
		cluster.network_init(net_iface,ns_ip,node_id)
		#Hook any other initialization methods here
	
	# BEGINNING OF SHARED FUNCTION DEFINITIONS
	
	
	
	""" Factor search must be able to handle large numbers without
	using too much RAM causing MemoryErrors. Therefore range() must not be
	used """
	
	def factor_search(beginning,end,comp_num):
		i = beginning
		factors = []
		while i <= end:
			if comp_num % i == 0:
				#We have found a factor
				factors.append(i)
			i += 1
		return factors
	
	# This function must be made available to the API
	
	slave_tasks_list['factor_search'] = factor_search
	
	# END OF SHARED FUNCTION DEFINITIONS

::

master_program.py

::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	
	import cluster
	import hashlib
	import time
	import sys
	import math
	
	
	def factor_list_empty(lst):
		for i in lst:
			if i:
				return False
		return True
	
	
	start_time = time.time()
	
	
	#Initialize the task scheduler
	CLUSTER_SIZE = 4 #Set to number of worker processes in the cluster.
	cluster.round_robin_init(CLUSTER_SIZE)
	
	composite_number = int(sys.argv[1])
	print "Finding non-trivial factors of " + str(composite_number)
	
	chunk_size = ((composite_number/2) - 1)/CLUSTER_SIZE
	print "Calculated chunk_size: " + str(chunk_size)
	# Avoid a chunk size of zero
	if chunk_size == 0:
		chunk_size = 1
			
	
	#create the work list for each node
	i = 2
	work_list = []
	while i <= (composite_number/2) + 1:
		tmp_list = []
		tmp_list.append(i)
		i += chunk_size
		tmp_list.append(i)
		i += 1
		work_list.append(tmp_list)
	
	print work_list
	
	factors_list = []
		
	
	task_count = 0
	emp_nodes = []
		
	for i in work_list:
		task_count += 1
		emp_nodes.append(cluster.concurrent_task('factor_search','t_'+str(task_count),i[0],i[len(i)-1],composite_number))
		
	for i in range(1,task_count+1):
		cluster.wait_for_task('t_'+str(i),emp_nodes[i-1])
		factors_list.append(cluster.get_output_from_task('t_'+str(i),emp_nodes[i-1]))
	
	
	print "Non trivial factors of " + str(composite_number) + " are..."	
	
	for i in range(0,len(factors_list)):
		for j in range(0,len(factors_list[i])):
			print factors_list[i][j]
	
	if factor_list_empty(factors_list):
		print "...none. " + str(composite_number) + " is prime."	
	
	delta_time = time.time() - start_time
	
	print "This factorization took " + str(delta_time) + " seconds."	
		

::
