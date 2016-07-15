Writing the slave (back-end) program
************************************

.. toctree::
   :maxdepth: 2
   
Setup
#####

All slave programs must begin by importing :mod:`cluster` into its own
namespace and importing :mod:`cluster_slave_headers` into the global namespace.

The first few lines of the slave program should look like this. ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	import cluster
	from cluster_slave_headers import *

::

After this, the :func:`slave_init` function must be defined. The default
one is as follows. ::

	# Define how the slave program should set itself up
	def slave_init(net_iface, ns_ip, node_id):
		cluster.network_init(net_iface,ns_ip,node_id)
		#Hook any other initialization methods here
		
::

This is the template initialization function for all distributed
programs using this API. Append any lines of code to this function that
you wish to be executed in order to setup the slave program.

Distributed Functions
#####################

Define a function to do work in the exact same way you would if the
function were running in a series processing program. After this, make 
it available to the distributed computing API by adding it to the 
:data:`slave_tasks_list` dictionary with the key set to the function name and
the value set to a reference to the function.

Here is an example of a simple function being made available to the
distributed computing API. ::

	""" Simple function that says hello and an appropriate message
	given the time of day """
	def say_hello(person_name, time_of_day):
		greeting_str = "Hello " + person_name + "."
		if time_of_day < 12:
			greeting_str += " Good morning."
		else:
			greeting_str += " Good afternoon."
	
		print "WORKING saying: " + greeting_str #Useful for debugging
		return greeting_str
	
	# This function must be made available to the API
	slave_tasks_list['say_hello'] = say_hello
	
::

Example
#######

Here is an example of a very simple slave program. The next section will
focus on writing a master program to use the functionality of the slave
program. ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	import cluster
	from cluster_slave_headers import *
	
	# Define how the slave program should set itself up
	def slave_init(net_iface, ns_ip, node_id):
		cluster.network_init(net_iface,ns_ip,node_id)
		#Hook any other initialization methods here
		
	""" Simple function that says hello and an appropriate message
	given the time of day """
	def say_hello(person_name, time_of_day):
		greeting_str = "Hello " + person_name + "."
		if time_of_day < 12:
			greeting_str += " Good morning."
		else:
			greeting_str += " Good afternoon."
	
		print "WORKING saying: " + greeting_str #Useful for debugging
		return greeting_str
	
	# This function must be made available to the API
	slave_tasks_list['say_hello'] = say_hello
	
::


LongTasks
#########

A LongTask is a task where multiple slave process are working to solve a
common problem and it is not known which one will be the first to obtain
a solution. This is useful for implementing brute-force algorithms.

The key to implementing a LongTask is defining it in as many subroutines
as possible. For example, here is the code to solve a partial sha512
hash collision without parallelization. ::

	def hash_collide(problem_string,n_zeros):
		while ((hashlib.sha512(problem_string).hexdigest())[0:n_zeros] != '0'*n_zeros):
			problem_string = problem_string + 'a'
		return problem_string
		
::

The same task, implemented for parallel deployment can be written as
follows. ::

	def hash_collide(hashCollider,problem_string,n_zeros):
		print "WORKING to solve: " + problem_string #Useful for debugging
		hashCollider.set_var('problem_string',problem_string)
		while ((hashlib.sha512(hashCollider.get_var('problem_string')).hexdigest())[0:n_zeros] != '0'*n_zeros):
			if hashCollider.run_task('hash_collide_part_0001'): # +++ Added a breakpoint here
				return None
		hashCollider.cluster_return(hashCollider.get_var('problem_string')) # Use cluster_return instead of return
	
	def hash_collide_part_0001(hashCollider):
		problem_string = hashCollider.get_var('problem_string') # +++ Get the variable
		problem_string = problem_string + 'a'                  # The subtask has now been wrapped
		hashCollider.set_var('problem_string',problem_string)   # +++ Put the variable back once it's been modified

::

All subroutines in the LongTask must take the parallel processing object
which they are working on as their first parameter. All other parameters
are the regular parameters for the function. Variables are created or
modified using the :func:`parallel_processing_object.set_var` method
with the first argument being the name of the variable and the second
argument being its value. Variables are retrieved from the parallel
processing object by calling :func:`parallel_processing_object.get_var`
with the first and only argument being the name of the variable to get.
The value of this variable is returned. Subroutines are called by
calling :func:`parallel_processing_object.run_task` and checking what
this method returns. If it returns ``True`` the LongTask must finish,
thus the "if" statement in the previous example.

A function in the slave program, which builds the parallel processing
object, must be defined. This function must build an object of class
:class:`cluster.LongTask`, add all the subroutines which it will use,
set its main task and possibly setup **master communication**. Finally,
this function must be made available to the API by adding it to the
dictionary :data:`slave_longtask_classes`.

The following code example defines (and exports to the API) a function
which will build a parallel processing object which will attempt to
solve a partial hash collision and will
stop when instructed to do so. ::

	def build_talking_hashCollider():
		talkingHashCollider = cluster.LongTask()
		talkingHashCollider.add_task('hash_collide',hash_collide)
		talkingHashCollider.add_task('hash_collide_part_0001',hash_collide_part_0001)
		talkingHashCollider.set_main_task('hash_collide')
		#Make it communicate
		talkingHashCollider.enable_master_comm()
		talkingHashCollider.set_master_server("PyroMaster")
		return talkingHashCollider
		
	slave_longtask_classes['talkingHashCollider'] = build_talking_hashCollider
	
::



