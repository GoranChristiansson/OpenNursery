#!/usr/bin/python3
#
#   arduino_list.py - make a list of all arduino's that are connected to this Raspberry
#
# v1 - 2021-01-09, Trees for Peace, G. Christiansson

import serial
import datetime
import time
import glob
import pickle


baud_rate = 9600                     # Must match Arduino baud rate
tout = 5                       # Seconds



def read_serial_data(serial):
    """
    Given a pyserial object (serial). Outputs a list of lines read in
    from the serial port
    """
    max_num_readings = 10
    serial.flushInput()
    
    serial_data = []
    readings_left = True
    timeout_reached = False
    
    while readings_left and not timeout_reached:
        serial_line = serial.readline()
        if serial_line == '':
            timeout_reached = True
        else:
            serial_data.append(serial_line)
            if len(serial_data) == max_num_readings:
                readings_left = False

    # print( str(serial_data[3]) )
    # return serial_data[3:]
    return(serial_data)
 
    

# portPaths - all /dev/ttyUSBx and /dev/ttyACMx
print("arduino_list.py - which Entomatic arduino's are connected ")

portPaths = []
for port in glob.glob('/dev/ttyUSB*') :
    portPaths.append( port )
for port in glob.glob('/dev/ttyACM*') :
    portPaths.append( port )

print( "These serial objects are connected")
print( portPaths )

serial_objs = []
for port in portPaths:
    ser = serial.Serial(port, baud_rate, timeout = tout)
    serial_objs.append( ser )

print(serial_objs)

time.sleep(2)    # wait until the arduinos start to send data
a_list = []
arduinoIDint = 0
for serial in serial_objs:
    print ("Reading serial data...")
    # print( serial.readline());

    serial_data = read_serial_data(serial)
    if len(serial_data) == 0:   
        print('Warning - empty data package')
        continue  # if there is no data in this package.
    print(serial.port)
    print(serial_data)
    arduinoIDint = serial_data[0][0]-48; 
    print( arduinoIDint )
    
    # Store this to a list so that we know which ttyUSB0 is which arduino
    # That is important so that we can load new software to each specific hardware
    # and so that we can change temperature setpoints for the right arduino.    
    # arduinoID = "1"
    a_list.append( [serial.port,str(arduinoIDint)] )


with open("arduino_list.pickle", 'wb') as f:
    pickle.dump( a_list, f)


#with open("arduino_list.pickle", 'rb') as f:
 #   a_list = pickle.load(f)