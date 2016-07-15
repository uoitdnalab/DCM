#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cluster
import Pyro4
import sys

srv = cluster.MasterServer()
cluster.network_init(sys.argv[1],sys.argv[2],sys.argv[3])
cluster.add_server_to_network(srv)
