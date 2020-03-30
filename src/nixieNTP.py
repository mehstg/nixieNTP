#! /usr/bin/python

"""nixieNTP.py: This script is designed to generate a NMEA GPRMC sentence with the correct system time/date and output via serial."""
"""This script has been tested with the Nixie QTC kit available from PV Electronics - http://http://www.pvelectronics.co.uk/"""

""" For NMEA sentence specifications, please visit - http://aprs.gids.nl/nmea/ """

__author__      = "Paul Braham"
__copyright__   = "Copyright 2012, Released under the GPLv3 License - more information at http://www.gnu.org/licenses/"

"""Updated 2020 to include a MQTT client to switch output on/off. Used with HomeAssistant"""

from functools import reduce
from operator import xor
import time
import datetime
import serial
import argparse
import paho.mqtt.client as mqtt

class mqttBool:
    def __init__(self):
        self.toggle = True

    def disable(self):
        self.toggle = False

    def enable(self):
        self.toggle = True

    def state(self):
        return self.toggle
toggle = mqttBool()

def main ():
    # Start of editable variables

    where = "5128.334,N,00003.100,W" # Fake co-ordinates - The nixie clock does not care about this
    serialPort = '/dev/ttyAMA0'
    baudRate = 4800 # Baud rate of serial connection
    serialParity = serial.PARITY_NONE # Serial Parity - Check PySerial for more info - http://pyserial.sourceforge.net/
    serialStopBits = serial.STOPBITS_ONE # Serial Stop Bits - Check PySerial for more info - http://pyserial.sourceforge.net/
    serialByteSize = serial.EIGHTBITS # Serial Byte Size - Check PySerial for more info - http://pyserial.sourceforge.net/


    # Argument parser - Allows nixieNTP to accept command line arguments in the form of:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v','--verbose', help='Prints GPRMC Sentence to STDOUT in addition to serial', action='store_true')
    parser.add_argument('-P','--port', help='Define serial port used, E.g. /dev/tty1', required=False)
    parser.add_argument('-m','--mqttbroker', help='Define MQTT broker address', required=True)
    parser.add_argument('-u','--mqttuser', help='Define MQTT auth username', required=True)
    parser.add_argument('-p','--mqttpass', help='Define MQTT auth password', required=True)
    args = parser.parse_args()
    

    # If command line argument --port is invoked, replace variable with contents
    if args.port:
        serialPort = args.port
    
    #Initiate connection to MQTT broker
    initiateMQTT(args.mqttbroker,1883,args.mqttuser,args.mqttpass)

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
        
        if toggle.state():
            #Write String to Serial
            ser.write(output.encode())
            if args.verbose:
                #Print String to STDOUT - For debugging
                print(output)
        if args.verbose:
            print("MQTT Toggle: " + toggle.state())
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


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("nixieclock/serial")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.payload)
    if (msg.payload == b'ON'):
        print("Turn Nixie Clock On")
        toggle.enable()
    elif (msg.payload == b'OFF'):
        print("Turn Nixie Clock Off")
        toggle.disable()
    else:
        print("No Match")


def initiateMQTT(broker,port,username,password):

    client = mqtt.Client()
    client.username_pw_set(username=username,password=password)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port, 60)

    #Start non blocking loop
    client.loop_start()


#Invoke main function
if __name__ == "__main__":
    main()

