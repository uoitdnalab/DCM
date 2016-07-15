import threading
import Pyro4
import netifaces
import re #For getting IP addresses
import socket #For transmitting files and large data sets.
import time #For benchmarking
import json #For decoding large data sets

#Import VariableServer and VariableClient into the 'cluster' namespace.
from variable_server import *
from variable_client import * 

# Set up the network
ethernet_ip = '' # IP address of the network interface card that faces the cluster
nameserver_ip = '' # IP address of the node which is hosting the nameserver
node_id = '' # Name of this node in the cluster
def network_init(iface, ns_ip, n_id):
	global ethernet_ip
	global nameserver_ip
	global node_id
	ethernet_ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
	nameserver_ip = ns_ip
	node_id = str(n_id)
	return ethernet_ip
	
def add_program_to_network(prgm_obj):
	daemon = Pyro4.Daemon(host=ethernet_ip)
	uri = daemon.register(prgm_obj)
	ns = Pyro4.locateNS(host=nameserver_ip)
	ns.register("worker.node_"+str(node_id),uri)
	daemon.requestLoop()
	
def add_server_to_network(server_obj):
	daemon = Pyro4.Daemon(host=ethernet_ip)
	uri = daemon.register(server_obj)
	ns = Pyro4.locateNS(host=nameserver_ip)
	ns.register("server.node_"+str(node_id),uri)
	daemon.requestLoop()
	
def connect_to_server(server_name):
	srv = Pyro4.Proxy("PYRONAME:server.node_"+str(server_name))
	return srv
		

def get_node_id():
	return node_id
	
def sequential_task(task_name, *task_args):
	# This is simple. TODO: run this task on the most optimal node.
	# TODO: Implement some kind of LOAD BALANCING
	employed_node_name = str(round_robin_next())
	employed_node = Pyro4.Proxy("PYRONAME:worker.node_"+employed_node_name)
	return employed_node.slave_do_seq_task(task_name, *task_args)

def broadcast_task(task_name, *task_args):
	employed_node_list = []
	for i in range(1,cluster_size+1):
		employed_node = Pyro4.Proxy("PYRONAME:worker.node_"+str(i))
		employed_node.slave_do_concurrent_task(task_name,"__btsk_"+str(i), *task_args)
		employed_node_list.append(employed_node)
		
	return employed_node_list
		
def wait_for_broadcast_task(node_lst):
	for idx in range(0,len(node_lst)):
		wait_for_task("__btsk_"+str(idx+1),node_lst[idx])

def broadcast_task_get_data(node_lst):
	outputs_list = []
	for idx in range(0,len(node_lst)):
		outputs_list.append(get_output_from_task("__btsk_"+str(idx+1),node_lst[idx]))
	
	return outputs_list	 
	
def concurrent_task(task_name,instance_name, *task_args):
	#task_controller = ConcurrentTaskMasterControl()
	#def task_wrapper(*task_args):
	#	task_controller.rx_data(task_name(*task_args))
		
	#task_obj = threading.Thread(target=task_wrapper, args=task_args)
	#task_obj.start()
	#task_controller.assign_thread(task_obj)
	#return task_controller
	
	#TODO: Implement some kind of LOAD BALANCING
	#employed_node_name = "1"
	employed_node_name = str(round_robin_next())
	employed_node = Pyro4.Proxy("PYRONAME:worker.node_"+employed_node_name)
	employed_node.slave_do_concurrent_task(task_name,instance_name, *task_args)
	return employed_node
	
def concurrent_task_file(task_name,instance_name,file_name, *task_args):
	employed_node_name = str(round_robin_next())
	# Do the file transfer - get the IP address from the PyRO nameserver
	ns = Pyro4.locateNS(host=nameserver_ip)
	loc = ns.lookup("worker.node_"+employed_node_name).location
	ip_search = re.search('\d*[.]\d*[.]\d*[.]\d*',loc)
	ip_ad = ip_search.group(0)

	employed_node = Pyro4.Proxy("PYRONAME:worker.node_"+employed_node_name)
	employed_node.slave_receive_file(file_name)
	
	# Now start sending the file
	f = open("shared_files/" + file_name, 'rb')
	sock = socket.socket()
	sock.connect((ip_ad, 9870))
	while True:
		chunk = f.read(65536)
		if not chunk:
			break
		sock.sendall(chunk)
	sock.close()
	
	# Make sure the file is completely copied??
	
	employed_node.slave_do_concurrent_task(task_name,instance_name, *task_args)
	return employed_node

# Transfer object as JSON string over socket
def get_large_output_from_task(tsk,nd):
	#DEBUG
	print "get_large_output_from_task() was called"
	conn_info = nd.get_large_output_from_task(tsk)
	#DEBUG
	print conn_info
	# Connect and start receiving data
	s = socket.socket()
	s.connect((conn_info['ip'],conn_info['port']))
	buf = s.recv(4096)
	data_str = ""
	while buf:
		data_str += str(buf)
		buf = s.recv(4096)
	s.close()
	# Deserialize JSON object and return
	#print data_str
	return json.loads(data_str)
	
	
	
def wait_for_task(tsk,nd):
	nd.wait_for_task(tsk)

def get_output_from_task(tsk,nd):
	return nd.get_output_from_task(tsk)
	
def cleanup_concurrent_task(tsk,nd):
	nd.cleanup_task(tsk)

def start_long_task(task_name,instance_name, *task_args):
	#TODO: Implement some kind of LOAD BALANCING
	#employed_node_name = "1"
	employed_node_name = str(round_robin_next())
	employed_node = Pyro4.Proxy("PYRONAME:worker.node_"+employed_node_name)
	# -- actually start the task
	employed_node.slave_start_long_task(task_name,instance_name,*task_args)
	return employed_node

def start_long_comm_task(task_name,instance_name,grp_name, *task_args):
	#TODO: Implement some kind of LOAD BALANCING
	#employed_node_name = "1"
	employed_node_name = str(round_robin_next())
	employed_node = Pyro4.Proxy("PYRONAME:worker.node_"+employed_node_name)
	# -- actually start the task
	employed_node.slave_start_long_comm_task(task_name,instance_name,grp_name,*task_args)
	return employed_node

	
def stop_long_task(tsk,nd):
	nd.slave_stop_long_task(tsk)

def finish_long_task(tsk,nd):
	nd.slave_finish_long_task(tsk)

def long_task_has_output(tsk,nd):
	return nd.slave_long_task_has_output(tsk)
	
def long_task_get_output(tsk,nd):
	return nd.slave_long_task_get_output(tsk)

def long_task_clean_up(tsk,nd):
	nd.slave_long_task_cleanup(tsk)



""" A Round-Robin task scheduler. Assign a task to each node and once
all nodes have been assigned a task keep repeating this process """
cluster_size = 0 # Global variable representing the number of nodes in the cluser
current_node = 1 # Global variable pointing to the node which will be assigned the task
def round_robin_init(s):
	global cluster_size
	cluster_size = s

def round_robin_next():
	global current_node
	if current_node <= cluster_size:
		nxt = current_node
		current_node += 1
	else:
		current_node = 1
		nxt = current_node
		current_node += 1
	
	return nxt
	
	



""" We need to have the option to launch a remote object server on the
master node so that it can be signaled when LongTasks complete """
	
class MasterServer:
	def __init__(self):
		self.finished_task_groups = {}
		
	def create_task_group(self,group_name):
		self.finished_task_groups[group_name] = {}
	
	
	def advertise_finished(self,tsk_name,tsk_group):
		#print "ADVERTISING FINISHED"
		self.finished_task_groups[tsk_group][tsk_name] = True
		
	def wait_for_one(self,tsk_group):
		#Block until one task from the group is completed
		while (True not in self.finished_task_groups[tsk_group].values()):
			pass
	
	def delete_task_group(self,group_name):
		del self.finished_task_groups[group_name]
		
	def list_groups(self):
		return self.finished_task_groups	


	
class ConcurrentTaskMasterControl:
	def __init__(self):
		self.thread_id = ''
		self.retval = ''
		
	def assign_thread(self,t):
		self.thread_id = t
	
	def wait_for_me(self):
		self.thread_id.join()
		return
	
	def get_output(self):
		return self.retval
		
	def rx_data(self,d):
		self.retval = d

""" This class is for large tasks which may need to be interrupted and
stopped because another node has already solved the problem. An example
of this is if another node has already solved a partial hash collision"""		
class LongTask:
	def __init__(self):
		self.flag_end = False
		""" Have the API user break their task down into as many
		functions as possible so that when each function is invoked
		we can check if we can quit the long task. The functions will
		be stored in a dictionary """
		self.function_dictionary = {}
		
		""" Have the same idea for data that lives in a long function """
		self.data_dictionary = {}
		
		""" The entry point for this task """
		self.main_task = ''
		
		""" The thread object we will call join() on when quitting the task """
		self.task_thread = ''
		
		""" The return value of the task """
		self.retval = ''
		
		""" Does the task have output or was it killed before it finished """
		self.hasOutput = False
		
		""" Does this task need to communicate back to a master server? Assume No. """
		self.master_server_comm = False
		
		# Server object with which it will communicate with
		self.master_server = ''
		
		# Group that task belongs to on server
		self.server_group = ''
		
		# The name of this task
		self.instance_name = ''
		
	def end_task(self):
		self.flag_end = True
		
	def start_task(self, *task_args):
		self.hasOutput = False # assume no output until we actually get it
		self.flag_end = False # we are calling start_task() so we don't want to end yet
		self.task_thread = threading.Thread(target=self.function_dictionary[self.main_task],args=task_args)
		self.task_thread.start()
		
	def add_task(self,name,func):
		self.function_dictionary[name] = func
		
	def get_var(self,name):
		return self.data_dictionary[name]
		
	def set_var(self,name,d):
		self.data_dictionary[name] = d
	
	def run_task(self,name):
		if self.flag_end is False:
			self.function_dictionary[name](self)
			return False
		else:
			return True # Start the ending for the thread
	
	def set_main_task(self, task_name):
		self.main_task = task_name
		
	def finish_task(self):
		self.task_thread.join()
	
	def has_output(self):
		return self.hasOutput
		
	def get_output(self):
		return self.retval
		
	def cluster_return(self,retval):
		self.retval = retval
		self.hasOutput = True # Because we now have output
		# Inform the master server if we need to
		if self.master_server_comm:
			#print "advertising finished"
			self.master_server.advertise_finished(self.instance_name,self.server_group)
		
	def enable_master_comm(self):
		self.master_server_comm = True
		
	def set_master_server(self,srvr):
		self.master_server = Pyro4.Proxy("PYRONAME:server.node_"+str(srvr))
		
	def set_group(self,grp):
		self.server_group = grp
		
	def set_name(self,n):
		self.instance_name = n	
		
	
