#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cluster
import sys
import importlib


temp_prgm_obj = importlib.import_module(sys.argv[1])
temp_prgm_obj.slave_init(sys.argv[2],sys.argv[3],str(sys.argv[4]))
print "adding one program"
cluster.add_program_to_network(temp_prgm_obj)
		


