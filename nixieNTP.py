#! /usr/bin/python
from operator import xor
import time
import datetime
import serial
import argparse

def main ():

	parser = argparse.ArgumentParser()
	parser.add_argument('-v','--verbose', help='Prints GPRMC Sentence to STDOUT in addition to serial', action='store_true')
	parser.add_argument('-p','--port', help='Define serial port used, E.g. /dev/tty1', required=False)
	args = parser.parse_args()
	
	print "Debug info, to be removed"
	print args
	
	#Fake Longitude/Latitude coordinates
	where = "5138.334,N,00003.740,W"

	if args.port:
		serialPort = args.port
	else:
		serialPort = '/dev/ttyAMA0'

	# configure the serial connections (This will differ depending on 
	#the Nixie Clock you are connecting to)
	ser = serial.Serial(
    	port=serialPort,
    	baudrate=4800,
    	parity=serial.PARITY_NONE,
    	stopbits=serial.STOPBITS_ONE,
   	bytesize=serial.EIGHTBITS
	)

	# Open Serial Port
	ser.open()
	ser.isOpen()

	while True:
		
		#Current Date and Time on System
		currTime = datetime.datetime.utcnow().strftime("%H%M%S.000")
		currDate = datetime.datetime.utcnow().strftime("%d%m%y")
		
		# Generate GPRMC and put in 'sentence' variable
		sentence =  generateGPRMCString(where,currDate,currTime)

		# Append XOR checksum to the end of the GPRMC Sentence
		output = sentence+calculateChecksum(sentence)
		
		#Write String to Serial
		ser.write(output)

		if args.verbose:
			#Print String to STDOUT - For debugging
			print output

		#Sleep for 1 second
		time.sleep(1)




def generateGPRMCString (where,date,time):
	#Format GPRMC string using the given date time and location information
	return "$GPRMC,"+time+",A,"+where+",0.0,0.0,"+date+",,A*"



def calculateChecksum (gprmcString):
	#Calculate and return checksum of inputted GPRMC String
	# Converts every character in the substring
	# between '$' and the '*' (exclusive)
	# in a sequence of integral values.
	nmea = map(ord, gprmcString[1:gprmcString.index('*')])

	# Reducing with xor the sequence
	checksum = reduce(xor, nmea)

	# Convert to Hex - Then String - Strip the '0x' from the start of the String - Messy, to be fixed
	return str(hex(checksum))[2:4]


#Invoke main function
if __name__ == "__main__":
    main()

