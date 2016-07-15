# %%%%%%%%%%% HEADER INFO ALWAYS NEEDS TO BE HERE %%%%%%%%%%%%%%%
																#
slave_tasks_list = {}											#
slave_longtask_objects = {}										#
slave_longtask_classes = {}

slave_interface_info = {}
																#
# %%%%%%%%%%%% END HEADER INFO %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# %%%%%%%%% FOOTER INFO ALWAYS NEEDS TO BE HERE %%%%%%%%%%%%%%%%%%%%%%%%%%
																		 #
import threading
import socket # used for file transmission								 #
import os # used for cleaning up files
import time #used for benchmarking
import json #For rapid transfer of large datasets
																		 #
running_tasks_dict = {}													 #
                                                                         #  
def slave_do_seq_task(task_name,*task_args):                             #
	return slave_tasks_list[task_name](*task_args)						 #			
	                                                                     #
def slave_concurrent_task(t_name, *task_args):							 #
	task_func = slave_tasks_list[t_name]                                 #
	task_controller = ConcurrentTaskControl()                    	     #
	def task_wrapper(*task_args):                                        #
		task_controller.rx_data(task_func(*task_args))                   #
		                                                                 #
	task_obj = threading.Thread(target=task_wrapper, args=task_args)     #
	task_obj.start()                      								 #
	task_controller.assign_thread(task_obj)                      		 #
	return task_controller                      						 #
																		 #
def slave_do_concurrent_task(t_name,instance_name,*task_args):			 #
	global running_tasks_dict											 #
	t_ctrl = slave_concurrent_task(t_name, *task_args)					 #
	running_tasks_dict[instance_name] = t_ctrl							 #


def slave_receive_file(file_name):
	# DEBUG
	print "Slave is recieving " + file_name
	# TODO: Run this in its own thread
	f = open("received_shared_files/" + file_name, "wb")
	s = socket.socket()
	s.bind(("",9870))
	s.listen(1)
	#DEBUG
	print "waiting for a connection"
	
	def rx_thread():
		sock, addr = s.accept()
		#DEBUG
		print "connection was accepted"
		begin_time = time.time()
	
		dat = sock.recv(65536)
		while (dat):
			f.write(dat)
			dat = sock.recv(65536)
		f.close()
		sock.close()
		s.close()
		print "File tranmssion time: " + str(time.time() - begin_time)
		
	rx_ctrl = threading.Thread(target=rx_thread)
	rx_ctrl.start()
																		 #
																		 #
def wait_for_task(tsk):													 #
	running_tasks_dict[tsk].wait_for_me()								 #
																		 #
																		 #
def get_output_from_task(tsk):											 #
	return running_tasks_dict[tsk].get_output()
	
def get_large_output_from_task(tsk):
	t_i = time.time()
	data_str = json.dumps(running_tasks_dict[tsk].get_output())
	#print data_str
	#print "serialization and transmission time: " + str(time.time() - t_i)
	s = socket.socket()
	#s.bind(("", 0)) #Let OS assign a port
	s.bind((slave_interface_info['ip'],0))
	s.listen(1)
	tx_ctrl = threading.Thread(target=send_output_thread, args=(s,data_str))
	tx_ctrl.start()
	conn_info = {}
	conn_info['ip'] = slave_interface_info['ip']
	conn_info['port'] = s.getsockname()[1]
	return conn_info								

# This thread sends the large output over a socket
def send_output_thread(sock, dat):
	print "waiting for a connection for dataset"
	#print "going to send " + dat
	active_conn, addr = sock.accept()
	print "connection received for dataset"
	active_conn.sendall(dat)
	active_conn.close()
	sock.close()
																		 #
def cleanup_task(tsk):													 #
	del running_tasks_dict[tsk]											 #
																		 #
																		 #
def slave_start_long_task(t_obj_name,instance_name,*task_args):			 #
	#Create a new instance of LongTask bound to identifier instance_name ##############
	slave_longtask_objects[instance_name] = slave_longtask_classes[t_obj_name]()	 #
	slave_longtask_objects[instance_name].set_name(instance_name)
	slave_longtask_objects[instance_name].start_task(slave_longtask_objects[instance_name],*task_args)

def slave_start_long_comm_task(t_obj_name,instance_name,grp_name,*task_args):			 #
	#Create a new instance of LongTask bound to identifier instance_name ##############
	slave_longtask_objects[instance_name] = slave_longtask_classes[t_obj_name]()	 #
	slave_longtask_objects[instance_name].set_name(instance_name)
	slave_longtask_objects[instance_name].set_group(grp_name)
	slave_longtask_objects[instance_name].start_task(slave_longtask_objects[instance_name],*task_args)

																		 #
def slave_stop_long_task(instance_name):								 #
	slave_longtask_objects[instance_name].end_task()					 #
																		 #
def slave_finish_long_task(instance_name):								 #
	slave_longtask_objects[instance_name].finish_task()					 #
																		 #
def slave_long_task_has_output(instance_name):							 #
	return slave_longtask_objects[instance_name].has_output()			 #
																		 #
def slave_long_task_get_output(instance_name):							 #
	return slave_longtask_objects[instance_name].get_output() 			 #
																		 #
def slave_long_task_cleanup(instance_name):
	del slave_longtask_objects[instance_name]																		 #
																		 #
																		 #
class ConcurrentTaskControl:                      						 #
	def __init__(self):     	      									 #
		self.thread_id = ''		                						 #
		self.retval = ''                      							 #		
																		 #
	def assign_thread(self,t):                      					 #
		self.thread_id = t                      						 #
																		 #
	def wait_for_me(self):                      						 #
		self.thread_id.join()                      						 #
		return                      									 #
																		 #
	def get_output(self):                      							 #
		return self.retval                      						 #
																		 #
	def rx_data(self,d):                      							 #		
		self.retval = d 												 #
																		 #
class ConcurrentTaskMasterControl:                      			     #
	def __init__(self):                      				 			 #
		#self.thread_ctrl_num = thread_ctrl_num             			 #
		self.retval = ''                      							 #		
																		 #
																		 #
	def wait_for_me(self, t_ctrl):                 						 #
		t_ctrl.wait_for_me()		             						 #
		return                      									 #
																		 #
	def get_output(self):                      							 #
		return self.thread_ctrl.get_output()							 #
																		 #
																		 #
																		 #
																		 #
# %%%%%%%%% END FOOTER INFO %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
