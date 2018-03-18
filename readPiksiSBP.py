#!/usr/bin/python
from sbp.client.drivers.pyserial_driver import PySerialDriver
import struct

HEADER_LEN = 5	#SBP message header length
header = []

ser = PySerialDriver("/dev/ttyUSB0")

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
	if msg_type == 526:	#Velocity in mm/s
		n = bytesToSInt(data[4:8])
		e = bytesToSInt(data[8:12])
		d = bytesToSInt(data[12:16])
		mode = (ord(data[21]) & 00000111)
		return (n[0],e[0],d[0], mode)	#Good data has mode>0
	

while 1:
	try:	#Attempt to read byte
		b = ord(ser.read(1))
	except:
		continue
	if (b == 0x55):	#Magic byte found
		try:	#Read entire message header
			header = ser.read(HEADER_LEN)
		except:
			print "Error reading header"
			continue
		try:	#Read entire message payload
			data = ser.read(ord(header[4]))
		except:
			print "Error reading data"
			continue

		msg_id = ord(header[0]) | (ord(header[1]) << 8)

		if len(data) > 1 and msg_id in [522, 526]:	#522=position,526=velocity

			ret = getData(data, msg_id)	#Get desired parameters from payload
			
			'''print "HEADER"
			for i in range(len(header)):
				print (ord(header[i])),
			print
			print "DATA"
			for i in range(len(data)):
				print (ord(data[i])),
			print'''

			print ret
			
