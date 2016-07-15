Cluster Deployment
******************

.. toctree::
   :maxdepth: 2
   

Once both the master and slave programs have been written, the parallel
computing system may now be deployed.

Name Server
###########

The first program which must be
started is the Pyro Name Server. To do this, go to the computer which
you have designated as being the name server (the one specified by the
second argument in :func:`cluster.network_init`) and run the command
:command:`python -m Pyro4.naming --host IPADDRESS` replacing IPADDRESS
with the IP address of the computer running the name server.

Master Server
#############

If the parallel computing system uses a master server (uses
communicating LongTasks) then the master server is the next program
which needs to be started. To start the master server run the command
:command:`python master_server.py "IFACE" "NAMESERVER_IP" "SERVERNAME"`
replacing IFACE, NAMESERVER_IP and SERVERNAME with the network
interface name, name server IP address and master server name,
respectively.

.. note:: This command must be executed in the directory that contains master_server.py

Slave Programs
##############

The slave programs can now be started on each node in the cluster by
running, on each node, the command
:command:`python cluster_starter.py SLAVE_PROGRAM "IFACE" "NAMESERVER_IP" "NODE_ID"`
replacing SLAVE_PROGRAM, IFACE, NAMESERVER_IP and NODE_ID with the slave
program name (without the .py), network interface name,
name server IP address and node ID, respectively.

.. warning:: node IDs must be unique, numerical, begin at 1 and increment only by 1. For example; 1,2,3,4 is a valid sequence of node IDs while 3,4,7,8 is not.

Master Program
##############

The master program should already be written for the current cluster
deployment so running it should be as simple as running the command
:command:`python MASTER_PROGRAM.py` replacing MASTER_PROGRAM with the
name of the master program.
