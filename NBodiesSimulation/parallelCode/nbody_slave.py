#!/usr/bin/env python
# -*- coding: utf-8 -*-

import planet
import threading #To use lock to protect data from data being manipulated by two threads at the same time.
import cluster
import os
import json
import numpy as np
from cluster_slave_headers import *

# The gravitational constant G
G = 6.67428e-11

# Define how the slave program should set itself up
def slave_init(net_iface, ns_ip, node_id):
	cluster.network_init(net_iface,ns_ip,node_id)
	#Hook any other initialization methods here

planets = [] #The list of planets assigned to this process

""" This function receives a planet object and stores it in this process """
planetsLock = threading.Lock() #Do not allow more than one thread to access planets at any given time
def rx_planet(new_planet_info):
	print "running rx_planet. Constructing a new planet"
	new_planet = planet.Planet(new_planet_info)
	print "[DEBUG] Trying to acquire planetsLock..."
	planetsLock.acquire()
	print "[DEBUG] ...acquired planetsLock"
	global planets
	for p in planets:
		p.addOtherPlanet(new_planet)
	planets.append(new_planet)
	print "Added planet " + str(len(planets))
	planetsLock.release()
	print "[DEBUG] released planetsLock"
	return "OK"

# This function must be made available to the API
slave_tasks_list['rx_planet'] = rx_planet

""" This function creates planets from a JSON file. It loads the list
from the JSON file and build planets for elements in the range
[start:end] """
def planets_from_json(filename, sectionIndex, nodes):
	global planets
	jsonFile = open(os.path.join("received_shared_files",filename))
	completePlanets = np.array(json.loads(jsonFile.read()))
	jsonFile.close()
	partialPlanets = np.array_split(completePlanets,nodes)[sectionIndex]
	partialPlanets = partialPlanets.tolist()
	for part_p in partialPlanets:
		new_planet = planet.Planet(part_p)
		for p in planets:
			p.addOtherPlanet(new_planet)
		planets.append(new_planet)
	
	
# This function must be made available to the API
slave_tasks_list['planets_from_json'] = planets_from_json

""" This function creates planets from a JSON file. It then calculates
how a section of these planets will act based on all the planets in this
file. """
def calculate_planets_json(filename,sectionIndex,nodes):
	planets = {}
	completePlanetObjects = []
	jsonFile = open(os.path.join("received_shared_files",filename))
	completePlanets = np.array(json.loads(jsonFile.read()))
	jsonFile.close()
	
	#Construct a planet.Planet object for all entries in this file
	for pinfo in completePlanets:
		completePlanetObjects.append(planet.Planet(pinfo))
	
	#print completePlanetObjects
	
	partialPlanets = np.array_split(completePlanetObjects,nodes)[sectionIndex]
	partialPlanets = partialPlanets.tolist()
	for part_p in partialPlanets:
		for p in completePlanetObjects:
			if part_p is p:
				continue
			
			part_p.addOtherPlanet(p)
			#p.addOtherPlanet(part_p)
		
		planets[part_p.planet_id] = part_p.dump_dictionary()
	
	return planets

# This function must be made available to the API
slave_tasks_list['calculate_planets_json'] = calculate_planets_json


""" This function receives a list of planets. These planets already
have their gravitational interactions (among themselves) calculated.
Therefore only their gravitational interactions among other planets
need to be calculated """
remotePlanetsLock = threading.Lock() #Do not allow more than one thread to access remote_planets at any given time.
def rx_remote_planet_list(new_planets_list):
	global planets
	remotePlanetsLock.acquire()
	remote_planets = []
	for p in new_planets_list:
		myPlanet = Planet(p) #Construct a planet object from the given information
		
		#Calculate interactions with already existing planets
		for original_planet in planets:
			original_planet.addOtherPlanet(myPlanet)
		
		remote_planets.append(myPlanet) #Add this to the list of planets
	
	planetsLock.acquire()
	planets = planets + remote_planets #Merge - add these planets to those already in this node.
	planetsLock.release()
	
	remotePlanetsLock.release()
	

# This function must be made available to the API
slave_tasks_list['rx_remote_planet_list'] = rx_remote_planet_list


""" This function prints information about the planets stored in this node """
def debug_planet_info():
	print " === DEBUG === "
	for p in planets:
		print " -------------------------------- "
		print "ID: " + p.planet_id
		print "Position: " + str(p.px) + "," + str(p.py)
		print "Force: " + str(p.fnet_x) + "," + str(p.fnet_y)

# This function must be made available to the API
slave_tasks_list['debug_planet_info'] = debug_planet_info

""" This function returns a dictionary containing information about the planets currently in this node.
This list can be read by the master node and passed to other slave nodes."""
def generate_remote_planet_list():
	remote_planet_list = {}
	for p in planets:
		planet_info = {}
		planet_info["fnet_x"] = p.fnet_x
		planet_info["fnet_y"] = p.fnet_y
		planet_info["px"] = p.px
		planet_info["py"] = p.py
		planet_info["mass"] = p.mass
		planet_info["id"] = p.planet_id
		remote_planet_list[p.planet_id] = planet_info
	
	return remote_planet_list

# This function must be made available to the API
slave_tasks_list['generate_remote_planet_list'] = generate_remote_planet_list


""" Merges two sets of gravitationally interacting planets """
def merge_planet_dictionary(pd1, pd2):
	print "merging " + str(pd1) + " and " + str(pd2)
	result_planets = {}
	for pd1_key in pd1:
		myPlanet = planet.Planet(pd1[pd1_key])
		for pd2_key in pd2:
			otherPlanet = planet.Planet(pd2[pd2_key])
			myPlanet.addOtherPlanet(otherPlanet)
		result_planets[pd1_key] = myPlanet.dump_dictionary()
	
	for pd2_key in pd2:
		myPlanet = planet.Planet(pd2[pd2_key])
		for pd1_key in pd1:
			otherPlanet = planet.Planet(pd1[pd1_key])
			myPlanet.addOtherPlanet(otherPlanet)
		result_planets[pd2_key] = myPlanet.dump_dictionary()
	
	return result_planets

# This function must be made available to the API
slave_tasks_list['merge_planet_dictionary'] = merge_planet_dictionary

""" Calculates how planet set pd1 is affected by pd2 but NOT vice-versa """
def half_merge_planet_dictionary(pd1,pd2):
	#print "HALF MERGE " + str(pd1) + " and " + str(pd2)
	print "BEGIN HALF-MERGE"
	result_planets = {}
	for pd1_key in pd1:
		myPlanet = planet.Planet(pd1[pd1_key])
		for pd2_key in pd2:
			otherPlanet = planet.Planet(pd2[pd2_key])
			myPlanet.addOtherPlanet(otherPlanet)
		result_planets[pd1_key] = myPlanet.dump_dictionary()
	
	print "END HALF-MERGE"
	return result_planets
#This function must be made available to the API
slave_tasks_list['half_merge_planet_dictionary'] = half_merge_planet_dictionary

def reset_slave():
	print "RESETTING..."
	global planets
	planets = []
	
# This function must be made available to the API
slave_tasks_list['reset_slave'] = reset_slave

