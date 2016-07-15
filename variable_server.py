#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import socket
import json

class VariableServer:
	def __init__(self,ip):
		self.bind_ip = ip
	
		
	def serve_var(self,var):
		def var_server_thread(sock_obj, var):
			active_conn, addr = sock_obj.accept()
			active_conn.sendall(json.dumps(var))
			active_conn.close()
			sock_obj.close()
		
		s = socket.socket()
		s.bind((self.bind_ip,0))
		s.listen(1)
		server_thread = threading.Thread(target=var_server_thread, args=(s,var))
		server_thread.start()
		#Return to the caller information about the variable being served
		conn_info = {}
		conn_info['ip'] = self.bind_ip
		conn_info['port'] = s.getsockname()[1]
		return conn_info

			
			
