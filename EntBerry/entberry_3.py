#!/usr/bin/python3
#
# EntBerry - Monitor all 6 arduino's and send the recorded data to the InfluxDB database, print some debug info to the command line
# 
# version 1 - 2020-12-16, Trees for Peace - Goran Christiansson
#
# inspiration from  https://gist.github.com/ttmarek/f3312eaf18a2e59398a2#file-arduino_serial-py
#
# version 2 - added logging to influxDB - starting with .bashrc
#
# version 3 - improved logging to influxDB - each arduino gets a separate set of columns in the database.
#      - "1-TA1" is temperature A1 of arduino #1. 
#      - need to look into unique running? 
#        Multiple instances at the same time may be problematic? 
#
#   %todo: read 12 temperature setpoints from file? 
#   


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
measurement_name = "entomatic_3"
 
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
    Given a list of serial lines (data). Removes all spacing characters.
    Returns the cleaned list of lists of digits.
    Given something like: ['0.5000,33\r\n', '1.0000,283\r\n']
    Returns: [[0.5,33.0], [1.0,283.0]]
    """
    clean_data = []
    
    for line in data:
        #line_data = re.findall("[-+]\d*\.\d*|\d*",str(line) ) # Find all digits
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
print("entberry_monitor.py - logging from entomatic arduino's to influxDB")

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

#print(serial_objs)

time.sleep(3)    # wait until the arduino is ready to read
# nano is ready after 2, UNO is ready after 3 seconds
print('Set temperature setpoints')
# Todo - read setpoints from separate file!
for s in serial_objs:
    s.write(b'28, 29\n')

influx_fieldnames = ['arduino_id', 'arduino_software_id','TA1', 'TA2','TA3','TA4','TA5','TavgA','TSetpointA','dutyCycleA',
                                                'TB1', 'TB2','TB3','TB4','TB5','TAvgB','TSetpointB','dutyCycleB']

# serial_objs = [1,2] #debugging tests.
# Now we loop forever and read serial strings and send formatted data to influxDB
#while(1):
# run for 30 minutes, then a new instance will be started by crontab
for i in range(100):
    for serial in serial_objs:
        print ("Reading serial data...")
        serial_data = read_serial_data(serial)
        #serial_data = [['1','18','1','2','3','4','5','10','20','99','-1.0','-2.2','3','4','5','10','20','99\n']]
        time.sleep(1)
        #print (len(serial_data))
        if len(serial_data) == 0:   
            print('Warning - empty data package')
            continue  # if there is no data in this package.
            
        #print ("Cleaning data...")
        clean_data =  clean_serial_data(serial_data)
        #print( clean_data )
     
        # Make a data-message of clean_data[0] - the first row of data.
        if len( clean_data ) > 1:
            # If we captured a few messages, skip the first one, which is probably incomplete
            store_data = clean_data[1]
        else:
            store_data = clean_data[0]
        #print(' Store data: ')

        # Check for 85C data - don't store to the database
        dataOK = True;
        for i in range(2,15):
            if( store_data[i] == 85):
                print(" Sensor data 85C is no real temperature - message discarded \n")
                print(" << ")
                print( store_data )
                print(" >> ")
                dataOK = False
            elif( store_data[i] == 127):
                print(" Sensor data -127C is no real temperature - message discarded \n")
                print(" << ")
                print( store_data )
                print(" >> ")
                dataOK = False
            elif( store_data[i] > 100):
                print(" Sensor data >100C is hopefully not real temperature - message discarded \n")
                print(" << ")
                print( store_data )
                print(" >> ")
                dataOK = False
                
        if( not dataOK):
            # don't proceed to data storage to the database
            continue
       
        #print(store_data)
        if len(store_data) <= 17:   
            print('Warning - dataset with too few numbers!')
            continue  # if there is not enough numbers in this message - wait for next.

        # take a timestamp for this measurement
        now = datetime.datetime.utcnow()

        
        # Build data message programmattically
        body2 = [
            {
            "measurement": measurement_name,
            "time": now,
            "fields": {
                "arduino_id": store_data[0],
            }
            }
        ]   
        # make fields dictionary, start with a clear one:
        fields_dict = {"a":"b"}
        fields_dict.clear()
        index = 0;
        id_prefix = str( int(store_data[0]))+'-'

        for field in influx_fieldnames:
            #print('Adding: ' + field)
            fields_dict[ id_prefix+field ] =  store_data[index]
            index+=1
    
        #print(fields_dict)
        body2[0]['fields'] = fields_dict
        print(serial.port + " : ")
        print(fields_dict)
        
        # write the measurement
        ifclient.write_points(body2)
    time.sleep(10)
 