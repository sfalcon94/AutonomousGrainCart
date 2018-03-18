#!/usr/bin/python
from sbp.client.drivers.pyserial_driver import PySerialDriver
import struct
import math

class PiksiSBP:

	HEADER_LEN = 5	#SBP message header length
	header = []

	def __init__(self, port):
		self.port = port
		self.latlon_valid = NaN	#Good gps fix = (>0)
		self.speed_valid = NaN	#Valid velocities = (>0)
		self.latitude = NaN
		self.longitude = NaN
		self.track = NaN	#Angle of deviation from North
		self.speed = NaN	#Resultant of velocity vectors in x,y, and z
		try:
			ser = PySerialDriver(self.port)
		except:
			print "Failed to open gps port"

	def next(self):
		b = NaN
		self.latlon_valid = 0
		self.speed_valid = 0
		while (self.latlon_valid and self.speed_valid) == 0:	#Required to see both messages per call to next()
			#MESSAGE START
			while b != 0x55:	#Loop until magic byte is read
				b = ord(ser.read(1))
			#READ HEADER
			try:	#Read entire message header
				header = ser.read(HEADER_LEN)
				msg_id = ord(header[0]) | (ord(header[1]) << 8)
			except:
				print "Error reading header"
				self.latlon_valid = self.speed_valid = 0
				break
			#READ DATA AND PARSE
			#POSITION
			if msg_id == 522:
				try:	#Read entire message payload
					data = ser.read(ord(header[4]))
				except:
					print "Error reading data"
					self.latlon_valid = 0
					break
				if len(data) > 1:
					ret = getData(data, msg_id)	#Get desired parameters from payload
					self.latitude = ret[0]
					self.longitude = ret[1]
					self.latlon_valid = ret[2]
			#VELOCITY
			else if msg_id = 531:
				try:	#Read entire message payload
					data = ser.read(ord(header[4]))
				except:
					print "Error reading data"
					self.speed_valid = 0
					break
				if len(data) > 1:
					ret = getData(data, msg_id)	#Get desired parameters from payload
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
	
def getData(data, msg_type):	#Retrieve desired parameters from within messages
	if msg_type == 522:	#Position solution
		lat = bytesToDbl([i for i in data[4:12]])
		lon = bytesToDbl([i for i in data[12:20]])
		fix = (ord(data[33]) & 00000111)
		return (lat[0], lon[0], fix)	#Good data has fix>0
	if msg_type == 531:	#x,y,z velocity in mm/s
		x_vel = bytesToSInt(data[4:8])
		y_vel = bytesToSInt(data[8:12])
		z_vel = bytesToSInt(data[12:16])
		mode = (ord(data[41]) & 00000111)
		#Calculate speed and track
		speed = sqrt(x_vel[0]**2 + y_vel[0]**2 + z_vel[0]**2)
		track = atan(y_vel[0]/x_vel[0]) #Angle of deviation from North
		return (speed, track, mode)	#Good data has mode>0