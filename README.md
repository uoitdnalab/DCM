# DCM - Distributed Computing Middleware

A Python module for writing distributed programs for a cluster of
inexpensive computers such as the Raspberry Pi.

 - Sphinx generated documentation can be found in the `Documentation`
directory. It can also be viewed online
[here](https://uoitdnalab.github.io/DCM) on GitHub.

 - An example of using this module for parallel simulation of the N-body
problem can be found in the `NBodiesSimulation` directory.

Dependencies
------------

Install the following packages from the Raspbian repositories.
Installing packages from pip can result in downloading a software
version which is incompatible with our API. Our tests used Raspbian
Jessie Lite.

* pyro4
* python2-pyro4
* python-netifaces

You will also need to install `python-serpent` from Raspbian stretch. To
do this add the line

`deb http://mirrordirector.raspbian.org/raspbian/ stretch main`

to `/etc/apt/sources.list`, run `sudo apt-get update` and then
`sudo apt-get -t stretch install python2-serpent`.

For running the NBodies example, numpy needs to be installed on all
nodes. It can be installed in Raspbian Jessie by running the command
`sudo apt-get install python-numpy`.

Running an Example
------------------

The following steps will run the `NBodiesSimulation` program on two
Raspberry Pis.

1. Copy this repository onto both Raspberry Pis.

2. On the master Pi, start the name server by running the command
`python -m Pyro4.naming --host ETH_IP` replacing `ETH_IP` with the IP
address of the network interface which faces the cluster.

3. On the master Pi, open a new terminal and enter the directory
`NBodiesSimulation/parallelCode` and copy into it the following files:

	* `cluster.py`
	* `cluster_slave_headers.py`
	* `cluster_starter.py`
	* `master_server.py`
	* `variable_client.py`
	* `variable_server.py`

4. On both the master and slave Pis, create the directory
`received_shared_files` under the `NBodiesSimulation/parallelCode`
directory.

5. On the master Pi, start a slave process by running the command
`python cluster_starter.py nbody_slave "NS_IFACE" "NS_IP" "1"`
replacing `NS_IFACE` with the network interface which connects this node
to the cluster (most likely `eth0`) and `NS_IP` with the IP address of
the name server (same as `ETH_IP` from step 2).

6. On the slave Pi, start a slave process by entering the
`NBodiesSimulation/parallelCode` directory and running the command
`python cluster_starter.py nbody_slave "NS_IFACE" "NS_IP" "2"`
replacing `NS_IFACE` and `NS_IP` with the same values as the previous
step.

7. On the master Pi, open a new terminal and enter the directory
`NBodiesSimulation/parallelCode`. Edit the file
`nbody_simple_master.py` and change the line `WORKER_NODES = 1` to
`WORKER_NODES = 2` as there are two nodes in our cluster. Also change
the line `cluster.network_init('eth0','192.168.137.100',99)` to
`cluster.network_init('NS_IFACE','ETH_IP',99)` replacing `NS_IFACE` and
`ETH_IP` with the same values from step 5.

8. On the master Pi, start the master process by running the command,
`python nbody_simple_master.py 1000planets.json`


### Troubleshooting ###

If when running the command
`python nbody_simple_master.py 1000planets.json` you encounter the error


	Traceback (most recent call last):
	  File "nbody_simple_master.py", line 36, in <module>
		reset_procs = cluster.broadcast_task("reset_slave")
	  File "/home/pi/DCM/NBodiesSimulation/parallelCode/cluster.py", line 59, in broadcast_task
		employed_node.slave_do_concurrent_task(task_name,"__btsk_"+str(i), *task_args)
	  File "/usr/lib/python2.7/dist-packages/Pyro4/core.py", line 160, in __call__
		return self.__send(self.__name, args, kwargs)
	  File "/usr/lib/python2.7/dist-packages/Pyro4/core.py", line 286, in _pyroInvoke
		self.__pyroCreateConnection()
	  File "/usr/lib/python2.7/dist-packages/Pyro4/core.py", line 346, in __pyroCreateConnection
		uri=resolve(self._pyroUri)
	  File "/usr/lib/python2.7/dist-packages/Pyro4/naming.py", line 357, in resolve
		nameserver=locateNS(uri.host, uri.port)
	  File "/usr/lib/python2.7/dist-packages/Pyro4/naming.py", line 297, in locateNS
		sock.sendto(BroadcastServer.REQUEST_NSURI, 0, (bcaddr, port))
	socket.error: [Errno 101] Network is unreachable


try adding the following code to the beginning of cluster.py under the
line `from variable_client import * `

	__old__Pyro4Proxy__ = Pyro4.Proxy

	def __new__Pyro4Proxy__(name_str):
		if name_str.startswith('PYRONAME:'):
			pyro_name = name_str.lstrip('PYRONAME:')
			ns = Pyro4.locateNS(host='ETH_IP')
			uri = ns.lookup(pyro_name)
			return __old__Pyro4Proxy__(uri)
		else:
			return __old__Pyro4Proxy__(name_str)

	Pyro4.Proxy = __new__Pyro4Proxy__

replacing `ETH_IP` with the address from step 2.
