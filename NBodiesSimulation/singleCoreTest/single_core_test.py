#!/usr/bin/env python

"""
This program simulates a system of planets and determines the
gravitational force on each planet due to the other planets. If the
parallel version is working correctly, it will produce the same results
as this program.

"""

import math
import sys
import json
import time

beginTime = time.time()

# The gravitational constant G
G = 6.67428e-11

planets = [] #List of planets in the simulation

#From fiftyexamples
def attraction(self, other):
	"""(Body): (fx, fy)
	
	Returns the force exerted upon this body by the other body.
	"""
	# Report an error if the other object is the same as this one.
	if self is other:
		raise ValueError("Attraction of object %r to itself requested" % self['id'])

	# Compute the distance of the other body.
	sx, sy = self['px'], self['py']
	ox, oy = other['px'], other['py']
	dx = (ox-sx)
	dy = (oy-sy)
	d = math.sqrt(dx**2 + dy**2)

	# Report an error if the distance is zero; otherwise we'll
	# get a ZeroDivisionError exception further down.
	if d == 0:
		raise ValueError("Collision between objects %r and %r" % (self['id'], other['id']))


	# Compute the force of attraction
	f = G * self['mass'] * other['mass'] / (d**2)

	# Compute the direction of the force.
	theta = math.atan2(dy, dx)
	fx = math.cos(theta) * f
	fy = math.sin(theta) * f
	return fx, fy


"""
#Add some planets...
#...first planet ...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 0.0
p["py"] = 0.0
p["mass"] = 5.9742 * 10**24
p["id"] = "0001"
planets.append(p)

#...second planet...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 0.0
p["py"] = 1.0
p["mass"] = 4.8685 * 10**24
p["id"] = "0002"
planets.append(p)

#...third planet...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 4.3
p["py"] = 3.1
p["mass"] = 870.8685 * 10**24
p["id"] = "0003"
planets.append(p)

#...fourth planet...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 1.2
p["py"] = 1.5
p["mass"] = 470.8685 * 10**24
p["id"] = "0004"
planets.append(p)

#...fifth planet...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 5.2
p["py"] = 1.5
p["mass"] = 470.8685 * 10**24
p["id"] = "0005"
planets.append(p)

#...sixth planet...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 15.2
p["py"] = 1.5
p["mass"] = 40.8685 * 10**24
p["id"] = "0006"
planets.append(p)

#...seventh planet...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 17.2
p["py"] = 1.5
p["mass"] = 940.8685 * 10**24
p["id"] = "0007"
planets.append(p)

#...eigth planet...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 7.2
p["py"] = 1.5
p["mass"] = 90.8685 * 10**24
p["id"] = "0008"
planets.append(p)

#...ninth planet...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 137.2
p["py"] = 1.5
p["mass"] = 9.8685 * 10**24
p["id"] = "0009"
planets.append(p)

#...tenth planet...
p = {}
p["fnet_x"] = 0.0
p["fnet_y"] = 0.0
p["px"] = 107.2
p["py"] = 1.5
p["mass"] = 99.8685 * 10**24
p["id"] = "0010"
planets.append(p)

print "[DEBUG]" + str(planets)
"""

#Load planets from a file
planetsFile = open(sys.argv[1],'r')
planets = json.loads(planetsFile.read())
planetsFile.close()

for this_planet in planets:
	for other_planet in planets:
		if this_planet is other_planet:
			continue
		#Calculate attraction
		fx,fy = attraction(this_planet,other_planet)
		this_planet["fnet_x"] = this_planet["fnet_x"] + fx
		this_planet["fnet_y"] = this_planet["fnet_y"] + fy

#Blank lines
for i in range(0,100):
	print ""

for pl in planets:
	print pl["id"] + " ---> " + str(pl["fnet_x"]) + " , " + str(pl["fnet_y"])


elapsedTime = time.time() - beginTime

print " #### ELAPSED TIME: " + str(elapsedTime) + " seconds"
