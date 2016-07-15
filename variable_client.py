#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import json

class VariableClient:
	def download_var(self,conn_info):
		s = socket.socket()
		s.connect((conn_info['ip'],conn_info['port']))
		buf = s.recv(4096)
		data_str = ""
		while buf:
			data_str += str(buf)
			buf = s.recv(4096)
		s.close()
		# Deserialize JSON object and return
		return json.loads(data_str)
