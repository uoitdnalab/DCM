import math
import random

# The gravitational constant G
G = 6.67428e-11

class Planet:
	
	
	def __init__(self,info_dictionary):
		
		if "fnet_x" in info_dictionary:
			self.fnet_x = info_dictionary["fnet_x"]
		else:
			self.fnet_x = 0.0
		
		if "fnet_y" in info_dictionary:
			self.fnet_y = info_dictionary["fnet_y"]
		else:
			self.fnet_y = 0.0
		
		self.planet_id = info_dictionary["id"]
		self.px = info_dictionary["px"]
		self.py = info_dictionary["py"]
		self.mass = info_dictionary["mass"]
	
	def addOtherPlanet(self,planet_x):
		#Calculate attraction
		fx,fy = self.attraction(planet_x)
		
		#Update this planet
		self.fnet_x = self.fnet_x + fx
		self.fnet_y = self.fnet_y + fy
		
		#Also update the other planet
		#planet_x.fnet_x = planet_x.fnet_x - fx
		#planet_x.fnet_y = planet_x.fnet_y - fy
	
	
	#From fiftyexamples
	def attraction(self, other):
		"""(Body): (fx, fy)
		
		Returns the force exerted upon this body by the other body.
		"""
		# Report an error if the other object is the same as this one.
		if self is other:
			raise ValueError("Attraction of object %r to itself requested" % self.name)

		# Compute the distance of the other body.
		sx, sy = self.px, self.py
		ox, oy = other.px, other.py
		dx = (ox-sx)
		dy = (oy-sy)
		d = math.sqrt(dx**2 + dy**2)

		# Report an error if the distance is zero; otherwise we'll
		# get a ZeroDivisionError exception further down.
		if d == 0:
			raise ValueError("Collision between objects %r and %r" % (self.name, other.name))


		# Compute the force of attraction
		f = G * self.mass * other.mass / (d**2)

		# Compute the direction of the force.
		theta = math.atan2(dy, dx)
		fx = math.cos(theta) * f
		fy = math.sin(theta) * f
		return fx, fy
	
	""" Returns the current state of this planet as a dictionary """
	def dump_dictionary(self):
		planet_info = {}
		planet_info["fnet_x"] = self.fnet_x
		planet_info["fnet_y"] = self.fnet_y
		planet_info["px"] = self.px
		planet_info["py"] = self.py
		planet_info["mass"] = self.mass
		planet_info["id"] = self.planet_id
		return planet_info

""" This method randomly generates n planets """
def generatePlanets(n):
	planetList = []
	for i in range(0,n):
		planet_info = {}
		planet_info["fnet_x"] = 0.0
		planet_info["fnet_y"] = 0.0
		planet_info["px"] = float(random.randint(-1000,1000))
		planet_info["py"] = float(random.randint(-1000,1000))
		planet_info["mass"] = float(random.randint(1000,1000000000))
		planet_info["id"] = str(i)
		planetList.append(planet_info)
	return planetList


