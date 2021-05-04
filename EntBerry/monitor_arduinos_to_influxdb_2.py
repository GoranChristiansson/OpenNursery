#!/usr/bin/python3
#
# EntBerry - Monitor all 6 arduino's and send the recorded data to the InfluxDB database, print some debug info to the command line
# 
# version 1 - 2020-12-16, Trees for Peace - Goran Christiansson
#
# inspiration from  https://gist.github.com/ttmarek/f3312eaf18a2e59398a2#file-arduino_serial-py


import serial
import re
import time
import glob


baud = 9600                     # Must match Arduino baud rate
timeout = 5                       # Seconds
filename = "data.csv"
max_num_readings = 5
num_signals = 6
 
# Details for InfluxDB and time stamping
import datetime
from influxdb import InfluxDBClient

# influx configuration - edit these
ifuser = "grafana"
ifpass = "grafana"
ifdb   = "home"
ifhost = "127.0.0.1"
ifport = 8086
measurement_name = "entomatic"
 
# connect to influx
ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)
 
def create_serial_obj(portPath, baud_rate, tout):
    """
    Given the port path, baud rate, and timeout value, creates
    and returns a pyserial object.
    """
    return serial.Serial(portPath, baud_rate, timeout = tout)


def read_serial_data(serial):
    """
    Given a pyserial object (serial). Outputs a list of lines read in
    from the serial port
    """
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

    print( serial_data )
    # print( str(serial_data[3]) )
    # return serial_data[3:]
    return(serial_data)
 
def is_number(string):
    """
    Given a string returns True if the string represents a number.
    Returns False otherwise.
    """
    try:
        float(string)
        return True
    except ValueError:
        return False
        
def clean_serial_data(data):
    """
    Given a list of serial lines (data). Removes all characters.
    Returns the cleaned list of lists of digits.
    Given something like: ['0.5000,33\r\n', '1.0000,283\r\n']
    Returns: [[0.5,33.0], [1.0,283.0]]
    """
    clean_data = []
    
    for line in data:
        line_data = re.findall("\d*\.\d*|\d*",str(line) ) # Find all digits
        line_data = [float(element) for element in line_data if is_number(element)] # Convert strings to float
        if len(line_data) >= 2:
            clean_data.append(line_data)
 
    return clean_data           
 
 
def gen_col_list(num_signals):
    """
    Given the number of signals returns
    a list of columns for the data.
    E.g. 3 signals returns the list: ['Time','Signal1','Signal2','Signal3']
    """
    col_list = ['Time']
    for i in range(1,num_signals+1):
        col = 'Signal'+str(i)
        col_list.append(col)
        
    return col_list
    
def map_value(x, in_min, in_max, out_min, out_max):
    return (((x - in_min) * (out_max - out_min))/(in_max - in_min)) + out_min
 
 
    

# portPaths - all /dev/ttyUSBx and /dev/ttyACMx

portPaths = []
for port in glob.glob('/dev/ttyUSB*') :
    portPaths.append( port )
for port in glob.glob('/dev/ttyACM*') :
    portPaths.append( port )

print( "Creating serial objects...")
print( portPaths )

serial_objs = []
for port in portPaths:
    serial_objs.append( create_serial_obj(port, baud, timeout) )

print(serial_objs)

time.sleep(2)    # wait until the arduino is ready to read
for s in serial_objs:
	s.write(b'23.45 26.76 \n')

print('Temperature setpoints are set')

# change this to while(1)
while(1):
    for serial in serial_objs:
        print ("Reading serial data...")
        serial_data = read_serial_data(serial)
        print (len(serial_data))
        print ("Cleaning data...")
        clean_data =  clean_serial_data(serial_data)
        print( clean_data )
     
        # Make a data-message of clean_data[0] - the first row of data.
        store_data = clean_data[0]
        print(' Store data: ')
        print(store_data)

        # take a timestamp for this measurement
        time = datetime.datetime.utcnow()

        # format the data as a single measurement for influx
        body = [
            {
            "measurement": measurement_name,
            "time": time,
            "fields": {
                "arduino_id": store_data[0],
                "arduino_software_id": store_data[1],
                "TA1": store_data[2],
                "TA2": store_data[3],
                "TA3": store_data[4],
                "TA4": store_data[5],
                "TA5": store_data[6],
                "TAvgA": store_data[7],
                "TSetpointA": store_data[8],
                "dutyCycleA": store_data[9],
                "TB1": store_data[10],
                "TB2": store_data[11],
                "TB3": store_data[12],
                "TB4": store_data[13],
                "TB5": store_data[14],
                "TAvgB": store_data[15],
                "TSetpointB": store_data[16],
                "dutyCycleB": store_data[17],

            }
            }
        ]
        
        # write the measurement
        ifclient.write_points(body)
 