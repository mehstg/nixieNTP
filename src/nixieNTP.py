#! /usr/bin/python

"""nixieNTP.py: This script is designed to generate a NMEA GPRMC sentence with the correct system time/date and output via serial."""
"""This script has been tested with the Nixie QTC kit available from PV Electronics - http://http://www.pvelectronics.co.uk/"""

""" For NMEA sentence specifications, please visit - http://aprs.gids.nl/nmea/ """

__author__      = "Paul Braham"
__copyright__   = "Copyright 2012, Released under the GPLv3 License - more information at http://www.gnu.org/licenses/"

from functools import reduce
from operator import xor
import time
import datetime
import serial
import argparse

def main ():

    
    # Start of editable variables

    where = "5128.334,N,00003.100,W" # Fake co-ordinates - The nixie clock does not care about this
    serialPort = '/dev/ttyAMA0'
    baudRate = 4800 # Baud rate of serial connection
    serialParity = serial.PARITY_NONE # Serial Parity - Check PySerial for more info - http://pyserial.sourceforge.net/
    serialStopBits = serial.STOPBITS_ONE # Serial Stop Bits - Check PySerial for more info - http://pyserial.sourceforge.net/
    serialByteSize = serial.EIGHTBITS # Serial Byte Size - Check PySerial for more info - http://pyserial.sourceforge.net/


    # Argument parser - Allows nixieNTP to accept command line arguments in the form of:
    # -v or --verbose - This prints the GPRMC sentence to STDOUT in addition to the serial output
    # -p or --port - This allows the user to specify the port used by nixieNTP - e.g. ./nixieNTP.py -p /dev/tty0
    parser = argparse.ArgumentParser()
    parser.add_argument('-v','--verbose', help='Prints GPRMC Sentence to STDOUT in addition to serial', action='store_true')
    parser.add_argument('-p','--port', help='Define serial port used, E.g. /dev/tty1', required=False)
    args = parser.parse_args()
    

    # If command line argument --port is invoked, replace variable with contents
    if args.port:
        serialPort = args.port
    

    # configure the serial connections (This will differ depending on 
    #the Nixie Clock you are connecting to)
    ser = serial.Serial(
        port=serialPort,
        baudrate=baudRate,
        parity=serialParity,
        stopbits=serialStopBits,
       bytesize=serialByteSize
    )

    # Open Serial Port
    #ser.open()
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
        ser.write(output.encode())

        if args.verbose:
            #Print String to STDOUT - For debugging
            print(output)

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

