Writing the master (front-end) program
****************************************

.. toctree::
   :maxdepth: 2

Setup
######

All master programs must begin by importing :mod:`cluster` into its own
namespace.

The first few lines of the master program should look like this. ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	import cluster

::

After this, the :func:`cluster.network_init` function must called. The
arguments are (network_interface, name server address, node_ID). The next
bit of code will demonstrate starting a master program on 'eth0' with a
name server IP address of 192.168.137.1 and a node ID of 99. ::

	
	cluster.network_init('eth0','192.168.137.1',99)
	
::

Now, the task scheduler must be initialized. This is done by calling
:func:`cluster.round_robin_init` with the number of slave processes running
as its only argument. The following bit of code will set up a cluster
with 3 slave processes. ::

	#Initialize the task scheduler
	cluster.round_robin_init(3)
	
::

Sequential Tasks
################

Tasks are executed sequentially (in series) by calling
:func:`cluster.sequential_task` with the first argument being the name
of the function that was made available to the API and the following
arguments, the arguments for the function. The following code example
would call the :func:`say_hello` function defined in the slave program
with the arguments "John Smith" and 12. ::

	print cluster.sequential_task('say_hello',"John Smith",12)
	
::

The function :func:`cluster.sequential_task` blocks until it returns
output.

Concurrent Tasks
################

Tasks are executed concurrently (in parallel) by calling
:func:`cluster.concurrent_task` with the first argument being the name
of the function that was made available to the API, the second argument
being a unique task identifier and the following arguments being the
arguments for the function defined in the slave program. The following
code example would call the :func:`say_hello` function defined in the 
slave program with a task ID of "t_1" and arguments "Mike" and 15. ::

	emp_node = cluster.concurrent_task('say_hello','t_1',"Mike",15)
	
::

Unlike :func:`cluster.sequential_task`, :func:`cluster.concurrent_task`
will immediately return an object of the slave process doing the work.
The program can then call :func:`cluster.wait_for_task` with the first
argument being the task ID and the second argument being the slave
process object. :func:`cluster.wait_for_task` will block until the task
returns output. Finally to retrieve output from the task, the program
must call :func:`cluster.get_output_from_task` with the first argument
being the task ID and the second argument being the slave process
object. This will return output from the function. The following code
would start the task :func:`say_hello` with a task ID of "t_1" and
arguments "Mike and 15. The program will then wait for the task to
finish and then finally print out any output. ::

	emp_node = cluster.concurrent_task('say_hello','t_1',"Mike",15)
	cluster.wait_for_task('t_1',emp_node)
	print cluster.get_output_from_task('t_1',emp_node)
	
::

Concurrent Tasks with files
###########################

Sometimes a file needs to be transfered onto one node because a task
executing on that node will need to read it. The API provides a
function called :func:`cluster.concurrent_task_file` which is available
to master programs which will copy a file onto the node which will
execute the task. To use this function, the master program calls
:func:`cluster.concurrent_task_file` with the first argument being
the function name, the second argument being the task ID and the third
argument being the file which is to be copied. All remaining arguments
are passed directly to the slave task. The file on the master node is
retrieved by name out of the **shared_files** directory and sent to the
slave node into its **received_shared_files** directory. Files names are
preserved. It is the responsibility of the slave program task which
uses this file to open the file out of the **recieved_shared_files**
directory and handle it appropriately.

.. warning:: This method does not check if the file is currently being used on the slave node, so use with extreme care. It is possible to modify a file which is currently being read by a slave task.

The following function call would call :func:`hello_world` with a
task ID of "t_1" and pass the file "example.txt" from the
**shared_files** directory on the master node to the
**received_shared_files** directory on the slave node. ::

	cluster.concurrent_task_file('hello_world','t_1','example.txt')

::



LongTasks
#########

The final type of task which this API handles is a task where multiple
slave process are working to solve a common problem and it is not known
which one will be the first to obtain a solution. This is useful for
implementing brute-force algorithms. There are two types of LongTasks - 
communicating and non-communicating.

Non-Communicating LongTasks
---------------------------

Non-Communicating :class:`LongTasks` do not notify a master server when
they are done their task. To spawn a non-communicating LongTask from a
master_program call :func:`cluster.start_long_task` with the first
argument being the name of the function which builds the parallel
processing object, the second argument being the LongTask ID and the
remaining arguments being the usual arguments for the task. This
function will immediately return a parallel processing object for the
given task. The master program can then call
:func:`cluster.stop_long_task` with the LongTask ID as the first
argument and the parallel processing object as the second argument. This
will signal the LongTask to stop. The master program then calls
:func:`cluster.finish_long_task` with the LongTask ID as the first
argument and the parallel processing object as the second argument. This
function will block until the LongTask is terminated. The master program
can then call :func:`cluster.long_task_has_output` with the LongTask ID 
as the first argument and the parallel processing object as the second
argument. This will return ``True`` only if the parallel process was
able to solve to problem. If there is a solution, the master program can
call :func:`cluster.long_task_get_output` with the LongTask ID as the
first argument and the parallel processing object
as the second argument. This will return the solution from the task. 
Finally, the master program should call
:func:`cluster.long_task_clean_up` with the LongTask ID as the first
argument and the parallel processing object as the second argument once
that specific LongTask is not going to be needed anymore. The following
code example illustrates these ideas by trying for 5 seconds to solve a
partial hash collision. ::

	emp_node = cluster.start_long_task('hashCollider','hash_collider_001', "I'm at UOIT",8)
	time.sleep(5)
	# Kill the task but first let it run for 5 seconds
	cluster.stop_long_task('hash_collider_001',emp_node)
	cluster.finish_long_task('hash_collider_001',emp_node)
	if cluster.long_task_has_output('hash_collider_001',emp_node):
		print cluster.long_task_get_output('hash_collider_001',emp_node)
	else:
		print "Sorry no output"
	# And clean up
	cluster.long_task_clean_up('hash_collider_001',emp_node)

::

Communicating LongTasks
-----------------------

Communicating LongTasks are similar to Non-Communicating LongTasks
except this time there is a **master server** which can receive a
message from one task notifying that a solution has been found and that
all other LongTasks in this group can be terminated. Before any
communicating LongTasks can be spawned a connection to a
**master server** must first be established. To do this call
:func:`cluster.connect_to_server` with the name of the **master server**
as its only argument. This will return an object representing the 
**master server**. Next, the **master server** must be aware of the
group of workers attempting to solve a problem. To create this group,
call :func:`master_server_object.create_task_group` with its only
parameter being its group name. Parallel processes may now be spawned.
To do so, call :func:`cluster.start_long_comm_task` with the first
argument being the name of the function which builds the parallel
processing object, the second argument being the LongTask ID, the third
argument being the group name of workers and the remaining arguments
being the usual arguments for the task itself. This function will return
an object representing the parallel process. With these slave processes
working at solving the problem, the master program must now wait for a
solution. The master program calls
:func:`master_server_object.wait_for_one` with its only argument being
the group of workers which it must wait for. This function blocks until
one worker from the group has solved the problem. After this, the
program execution proceeds in the same manner as if it were a
non-communicating task; :func:`cluster.stop_long_task` is called for
each task, then, :func:`cluster.finish_long_task` is called for each
task. After this, each worker is check for output with
:func:`cluster.long_task_has_output` and any outputs are read with
:func:`cluster.long_task_get_output`. Finally, everything is cleaned up
by calling :func:`cluster.long_task_clean_up` for each worker. The
following example uses communicating LongTasks to have multiple workers
attempting to solve partial hash collisions for different strings and
whichever solution is obtained first is displayed. ::

	#First we will need a connection to our master server to know when one task is completed
	master_server = cluster.connect_to_server("PyroMaster")
	#Next we will need to inform the master server about our group of workers
	master_server.create_task_group('miners')
	#Now we can start working --- let's run multiple parallel tasks
	emp_node_1 = cluster.start_long_comm_task('talkingHashCollider','hash_collider_t1', 'miners', "Hello from UOIT", 12)
	emp_node_2 = cluster.start_long_comm_task('talkingHashCollider','hash_collider_t2', 'miners', "Hello from ACE" , 3)
	emp_node_3 = cluster.start_long_comm_task('talkingHashCollider','hash_collider_t3', 'miners', "Hello from ENG" , 5)
	emp_node_4 = cluster.start_long_comm_task('talkingHashCollider','hash_collider_t4', 'miners', "Hello from ERC" , 13)
	
	
	# --- Wait until work is finished
	master_server.wait_for_one('miners')
	
	# --- As soon as the work is done kill all the unfinished tasks
	cluster.stop_long_task('hash_collider_t1',emp_node_1)
	cluster.finish_long_task('hash_collider_t1',emp_node_1)
	cluster.stop_long_task('hash_collider_t2',emp_node_2)
	cluster.finish_long_task('hash_collider_t2',emp_node_2)
	cluster.stop_long_task('hash_collider_t3',emp_node_3)
	cluster.finish_long_task('hash_collider_t3',emp_node_3)
	cluster.stop_long_task('hash_collider_t4',emp_node_4)
	cluster.finish_long_task('hash_collider_t4',emp_node_4)
	
	
	
	#Now display our computed data
	if cluster.long_task_has_output('hash_collider_t1',emp_node_1):
		print cluster.long_task_get_output('hash_collider_t1',emp_node_1)
	else:
		print "Sorry no output"
	
	if cluster.long_task_has_output('hash_collider_t2',emp_node_2):
		print cluster.long_task_get_output('hash_collider_t2',emp_node_2)
	else:
		print "Sorry no output"
		
	if cluster.long_task_has_output('hash_collider_t3',emp_node_3):
		print cluster.long_task_get_output('hash_collider_t3',emp_node_3)
	else:
		print "Sorry no output"
	
	if cluster.long_task_has_output('hash_collider_t4',emp_node_4):
		print cluster.long_task_get_output('hash_collider_t4',emp_node_4)
	else:
		print "Sorry no output"
	
	
	#And finally clean up
	cluster.long_task_clean_up('hash_collider_t1',emp_node_1)
	cluster.long_task_clean_up('hash_collider_t2',emp_node_2)
	cluster.long_task_clean_up('hash_collider_t3',emp_node_3)
	cluster.long_task_clean_up('hash_collider_t4',emp_node_4)

::

Broadcast Tasks
###############

Broadcast tasks are procedures which are executed on all slave nodes in
the network. Whenever a master program calls a **broadcast task**,
the task is executed on all slave nodes. The execution is asynchronous -
this call does not block. The call returns a list of nodes running the
broadcast task. The master program may now use this list to wait for the
broadcast task to finish and to get output from it. To implement a
broadcast task, the task must first be created and exported in the slave
program in the exact same way in which a concurrent task would be
created and exported. The master program must then call 
:func:`cluster.broadcast_task` with the first argument being the
exported name of the task and any remaining arguments being specific
arguments for the function itself. The function will then return a list
of nodes running the task. The master program may now call
:func:`cluster.wait_for_broadcast_task` with its first and only argument
being the list returned from :func:`cluster.broadcast_task`. This call
will block until all slave nodes have finished the task.

.. warning:: As of the current implementation, the master program should wait for all broadcast tasks to finish before attempting to start any new ones.

The master program may now call
:func:`cluster.broadcast_task_get_data` with its first and only argument
being the list returned from :func:`cluster.broadcast_task`. This will
return a list of outputs from the functions which were executed in
broadcast fashion on the slave nodes.

.. warning:: The order of the outputs in the returned list should not be relied upon. Any master program which needs to know which slave node returned which data must have the slave node ID returned from the broadcast task along with the wanted (payload) data.	

Example
-------

A slave program: ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	
	""" This program will generate a random number between 1 and 100
	whenever get_random is called() """
	
	import cluster
	import hashlib
	import time
	import sys
	import random
	
	from cluster_slave_headers import *
	
	
	# Define how the slave program should set it's self up
	def slave_init(net_iface, ns_ip, node_id):
		cluster.network_init(net_iface,ns_ip,node_id)
		#Hook any other initialization methods here
	
	# BEGINNING OF SHARED FUNCTION DEFINITIONS
	
	def get_random():
		return random.randint(1,100)
	
	slave_tasks_list['get_random'] = get_random
	
	# END OF SHARED FUNCTION DEFINITIONS

::

A master program: ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	
	import cluster
	import hashlib
	import time
	import sys
	
	
	#Initialize the task scheduler
	cluster.round_robin_init(3)
	
	#Do a broadcast task
	procs = cluster.broadcast_task('get_random')
	
	#Wait for it to finish
	cluster.wait_for_broadcast_task(procs)
	
	#Display the output
	print cluster.broadcast_task_get_data(procs)

::

Would (for example, random numbers will vary) output: ::

	[31, 11, 45]

::


Moving large datasets with VariableServer and VariableClient
############################################################

When moving small pieces of data, such as short strings or integers,
between nodes using this API, it is common and acceptable practice to
either pass them as parameters to a function or read them as return
values from a function. This methodology can, however, be too slow
for transferring larger pieces of data, such as long lists. In this
case, it is better for the function wishing to send the variable to run
a VariableServer and the node receiving the data can run a
VariableClient. The link to the data is passed between nodes by
traditional means such as a function return value or an argument to a
function. VariableClients are created by calling the
:func:`cluster.VariableClient` constructor with no arguments and
VariableServers are created by calling the
:func:`cluster.VariableServer` constructor with the IP address facing
the cluster as its only argument. Calling
:func:`VariableServer.serve_var` with the variable to be sent as its
only argument will return a link to that variable. Calling
:func:`VariableClient.download_var` with the previously mentioned link
as its only parameter will return the variable that is being served.
Once the download is complete the variable will no longer be served.

The following example shows how a long list is traditionally passed
between nodes. This is the slow method. During tests, it took
approximately 47 seconds to run on a single node Raspberry Pi model B. 

A master program: ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	
	import cluster
	import time
	
	
	# Begin timing the task
	start_time = time.time()
	
	iface_ip = cluster.network_init("eth0", "192.168.137.100", "99")
	
	#Initialize the task scheduler
	CLUSTER_SIZE = 1
	cluster.round_robin_init(CLUSTER_SIZE)
	
	emp_node = cluster.concurrent_task('give_list','t_1')
	print "Task has been started"
	print "Waiting for task to finish"
	cluster.wait_for_task('t_1',emp_node)
	print "Task is finished"
	rand_list = cluster.get_output_from_task('t_1',emp_node)
	
	#Cleanup
	cluster.cleanup_concurrent_task('t_1',emp_node)
	
	print rand_list
	
	print "Time to run program: " + str(time.time() - start_time)


::

A slave program: ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	
	import cluster
	import random
	
	from cluster_slave_headers import *
	
	#Global variable which will become the object representing the VariableServer
	var_srv = ""
	
	# Define how the slave program should set it's self up
	def slave_init(net_iface, ns_ip, node_id):
		slave_interface_info['ip'] = cluster.network_init(net_iface,ns_ip,node_id)
		#Hook any other initialization methods here
	
	
	# BEGINNING OF SHARED FUNCTION DEFINITIONS
	
	def give_list():
		rand_list = []
		for i in range(0,250000):
			rand_list.append(random.randint(0,100))
	
		return rand_list
		
	
	# These functions must be made available to the API
	
	slave_tasks_list['give_list'] = give_list
	
	# END OF SHARED FUNCTION DEFINITIONS

	
::

The following example shows how the same task can be accomplished much
quicker using a VariableServer and a VariableClient. During tests, it took
approximately 19 seconds to run on a single node Raspberry Pi model B.

A master program: ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	
	import cluster
	import time
	
	
	# Begin timing the task
	start_time = time.time()
	
	iface_ip = cluster.network_init("eth0", "192.168.137.100", "99")
	# Create a variable client for the receiving of large datasets
	variable_client = cluster.VariableClient()
	
	#Initialize the task scheduler
	CLUSTER_SIZE = 1
	cluster.round_robin_init(CLUSTER_SIZE)
	
	emp_node = cluster.concurrent_task('give_list','t_1')
	print "Task has been started"
	print "Waiting for task to finish"
	cluster.wait_for_task('t_1',emp_node)
	print "Task is finished"
	rand_list_link = cluster.get_output_from_task('t_1',emp_node)
	rand_list = variable_client.download_var(rand_list_link)
	
	#Cleanup
	cluster.cleanup_concurrent_task('t_1',emp_node)
	
	print rand_list
	
	print "Time to run program: " + str(time.time() - start_time)

	
::

A slave program: ::

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	
	import cluster
	import random
	
	from cluster_slave_headers import *
	
	#Global variable which will become the object representing the VariableServer
	var_srv = ""
	
	# Define how the slave program should set it's self up
	def slave_init(net_iface, ns_ip, node_id):
		slave_interface_info['ip'] = cluster.network_init(net_iface,ns_ip,node_id)
		#Hook any other initialization methods here --- Create the VariableServer
		global var_srv
		var_srv = cluster.VariableServer(slave_interface_info['ip'])
	
	
	# BEGINNING OF SHARED FUNCTION DEFINITIONS
	
	def give_list():
		rand_list = []
		for i in range(0,250000):
			rand_list.append(random.randint(0,100))
	
		return var_srv.serve_var(rand_list)
		
	
	# These functions must be made available to the API
	
	slave_tasks_list['give_list'] = give_list
	
	# END OF SHARED FUNCTION DEFINITIONS
	
::
