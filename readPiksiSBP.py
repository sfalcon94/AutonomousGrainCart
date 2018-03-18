#!/usr/bin/python
from sbp.client.drivers.pyserial_driver import PySerialDriver
import struct
import math

HEADER_LEN = 5	#SBP message header length

class PiksiSBP:
	def __init__(self, port):
		self.port = port
		self.latlon_valid = 0	#Good gps fix = (>0)
		self.speed_valid = 0	#Valid velocities = (>0)
		self.latitude = 0
		self.longitude = 0
		self.track = 0	#Angle of deviation from North
		self.speed = 0	#Resultant of velocity vectors in x,y, and z
		try:
			self.ser = PySerialDriver(self.port)
		except:
			print "Failed to open gps port"

	def next(self):
		b = None
		self.latlon_valid = 0
		self.speed_valid = 0
		while (self.latlon_valid and self.speed_valid) == 0:	#Required to see both messages per call to next()
			#MESSAGE START
			while b != 0x55:	#Loop until magic byte is read
				b = ord(self.ser.read(1))
			#READ HEADER
			try:	#Read entire message header
				header = self.ser.read(HEADER_LEN)
				msg_id = ord(header[0]) | (ord(header[1]) << 8)
			except:
				print "Error reading header"
				break
			#READ DATA AND PARSE
			#POSITION
			if msg_id == 522:
				print "Found 522"
				try:	#Read entire message payload
					data = self.ser.read(ord(header[4]))
				except:
					print "Error position reading data"
					self.latlon_valid = 0
					break
				if len(data) == 34:
					ret = getParams(data, msg_id)	#Get desired parameters from payload
					self.latitude = ret[0]
					self.longitude = ret[1]
					self.latlon_valid = ret[2]
			#VELOCITY
			if msg_id == 526:
				print "Found 526"
				try:	#Read entire message payload
					data = self.ser.read(ord(header[4]))
				except:
					print "Error reading velocity data"
					self.speed_valid = 0
					break
				if len(data) == 22:
					ret = getParams(data, msg_id)	#Get desired parameters from payload
					self.speed = ret[0]
					self.track = ret[1]
					self.speed_valid = ret[2]


def bytesToDbl(b):	#Convert 8 byte list into double
	result = 0;
	result = struct.unpack('d',"".join(b));  
	return result;

def bytesToSInt(b):	#Convert 4 byte list into signed integer
	result = 0;
	result = struct.unpack('i',bytearray("".join(b)));  
	return result;
	
def getParams(data, msg_type):	#Retrieve desired parameters from within messages
	if msg_type == 522:	#Position solution
		lat = bytesToDbl([i for i in data[4:12]])
		lon = bytesToDbl([i for i in data[12:20]])
		fix = (ord(data[33]) & 00000111)
		return (lat[0], lon[0], fix)	#Good data has fix>0
	if msg_type == 526:	#Velocity in mm/s
		n = bytesToSInt(data[4:8])
		e = bytesToSInt(data[8:12])
		d = bytesToSInt(data[12:16])
		mode = (ord(data[21]) & 00000111)
		#Calculate speed and track
		speed = math.sqrt(n[0]**2 + e[0]**2 + d[0]**2)
		try:
			track = math.atan(e[0]/n[0]) #Angle of deviation from North
		except ZeroDivisionError:
			if e[0] > 0:
				track = 90
			else:
				track = -90
		return (speed, track, mode) #Good data has mode>0
