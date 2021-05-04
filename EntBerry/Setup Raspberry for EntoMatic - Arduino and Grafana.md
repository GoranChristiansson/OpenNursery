# Setup Raspberry for Entomatic

Trees for Peace - Goran Christiansson - 2020-12-16

## Arduino programming

We need to program all the arduino's that are connected to the Raspberry master computer. 

From the command line. (based on [Arduino Hacking from the Command Line | Raspberry VI](http://www.raspberryvi.org/stories/arduino-cli.html))

Terminal commands:

> $ sudo apt-get install build-essential

Now install the Arduino stuff:

> $ sudo apt-get install arduino arduino-core arduino-mk

We need to create a "Makefile" file in the folder where we have the Arduino source code:

```Makefile
ARDUINO_DIR  = /usr/share/arduino
USER_LIB_PATH = /home/christiansson/Arduino/libraries
ARDUINO_LIBS = DallasTemperature OneWire
BOARD_TAG    = uno
ARDUINO_PORT = /dev/ttyACM0

include /usr/share/arduino/Arduino.mk
```

Note: The USER_LIB_PATh is to where yyou have installed the DallasTemperature and OneWire libraries.
on the raspberry it is: USER_LIB_PATH = /home/pi/sketchbook/libraries

See separate file for intallation of those libraries.

Now we can compile/build .ino files into .hex files and send them to the arduino unit.

> $ sudo make upload

### Potential problems

: DallasTemperature - some versions use a function called yield(); that is not recognized by the arduino-mk. Comment this out. line 446:

```DallasTemperature.cpp
 while (!isConversionComplete() && (millis() - start < MAX_CONVERSION_TIMEOUT ))
    {
      //yield();
    }
```

Serial speed: For uploading the compiled program into the Arduino, sometimes there is a speed mismatch.

The Entomatic Prototype using Arduino nano 328 with old bootloader, the speed is 57600 baud - which we have to mention explicitly in the Makefile:

```Makefile
BOARD_TAG    = nano
ARDUINO_PORT = /dev/ttyUSB0
AVRDUDE_ARD_BAUDRATE = 57600
```

Todo: We need to address the processor type also for the nano:   now avrdude has " -p atmega168 "

## Arduino serial monitoring using minicom (optional)

```
$ sudo apt-get install minicom
$ minicom -D /dev/ttyACM0 -b 9600
```

Minicom is a separate tool to send and receive data on the serial port.

Use `CTRL-A` to initiate a command sequence. `CTRL-A X` is exit. `CTRL-A O` is configuration ("*O*ptions") where you can configure flow control and such.

## Database setup InfluxDB

see [Getting Started with Python and InfluxDB | InfluxData](https://www.influxdata.com/blog/getting-started-python-influxdb/)

Install influxdb with the package installer.



You have to disable authentication

Then you setup a database called "home" with a user called "grafana" who can read from the database:

---

```roboconf
[http]

# Determines whether HTTP endpoint is enabled.

  enabled = true

# The bind address used by the HTTP servic

  bind-address = ":8086"

# Determines whether user authentication is enabled over HTTP/HTTPS.

   auth-enabled = false
  #auth-enabled = true


```

```InfluxDB
create database home
use home

create user grafana with password 'grafana' with all privileges
grant all privileges on home to grafana

show users

user admin

---- -----

grafana true
```

The influxDB runs on the RaspberryPi (or host PC). 

Then the logging is done on a 5-10 minute interval. 

```python
# Details for InfluxDB and time stamping
from influxdb import InfluxDBClient
import datetime

# influx configuration - database user for logging
ifuser = "grafana"
ifpass = "grafana"
ifdb = "home"
ifhost = "127.0.0.1"
ifport = 8086
measurement_name = "entomatic"

# connect to influx
ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)
```

```python
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
```





When you have logged some data - use the influx command line interface to check what you have logged:

```bash
$ influx
> use home
Connected to http://localhost:8086 version 1.6.4
InfluxDB shell version: 1.6.4
> use home
Using database home
> show measurements
name: measurements
name
----
entomatic
> select * from entomatic limit 10
name: entomatic
time                TA1   TA2   TA3   TA4   TA5   TAvgA TAvgB TB1   TB2   TB3   TB4   TB5   TSetpointA TSetpointB arduino_id arduino_software_id dutyCycle dutyCycleA dutyCycleB relayOn t1 t2 t3 t4 tSetpoint
----                ---   ---   ---   ---   ---   ----- ----- ---   ---   ---   ---   ---   ---------- ---------- ---------- ------------------- --------- ---------- ---------- ------- -- -- -- -- ---------
1608189514837264128 16    16.56 16.37 16.81 17    16.58 16.15 15.94 15.5  16.69 16.44 16.06 0          0          7          17                            0          0                              
1608189539844089088 16    16.56 16.31 16.81 17    16.56 16.17 16    15.5  16.62 16.44 16.06 0          0          7          17                            0          0                              
1608189564849385984 16    16.56 16.31 16.81 16.94 16.56 16.12 15.94 15.5  16.69 16.44 16    0          0          7          17                            0          0                              
1608189589858685952 16.06 16.56 16.31 16.81 17    16.56 16.12 15.94 15.5  16.69 16.44 16    0          0          7          17                            0          0                              
1608189614861414912 16    16.56 16.31 16.81 17    16.56 16.17 16    15.5  16.69 16.44 16.06 0          0          7          17                            0          0                              
1608194104833602816 16    16.5  16.44 16.87 17.06 16.6  15.96 15.81 15.25 16.69 16.37 15.69 0          0          7          17                            0          0                              
1608194129843565056 16.06 16.5  16.44 16.81 17.06 16.58 15.96 15.81 15.31 16.69 16.37 15.69 0          0          7          17                            0          0                              
1608194154847096832 16.06 16.56 16.37 16.87 17    16.6  15.98 15.88 15.31 16.69 16.37 15.69 0          0          7          17                            0          0                              
1608194179856688896 16.06 16.56 16.44 16.87 17    16.62 15.96 15.81 15.25 16.69 16.37 15.69 0          0          7          17                            0          0                              

```

Test that you can read data from separate arduino_id units:

```bash
> select TA2 from entomatic where arduino_id = 7
> name: entomatic
> time                TA2

----                ---

1608189514837264128 16.56
1608189539844089088 16.56
1608189564849385984 16.56
1608189589858685952 16.56
1608189614861414912 16.56
1608194104833602816 16.5
1608194129843565056 16.5
1608194154847096832 16.56
1608194179856688896 16.56
1608194204859528192 16.5
1608194539376964096 16.5
1608194564384105984 16.5
1608194589389661952 16.5
1608194614396090112 16.5
1608194639401554176 16.5

> select TA2 from entomatic where arduino_id = 5
> 
> 

```



## Plotting with Grafana

The temperature plotting is done with Grafana in a browser window.



Alternative 1 - install grafana in the "OS" for everybody

```bash
sudo apt-get install -y apt-transport-https
sudo apt-get install -y software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

# Add this repository for stable releases:
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

# install
sudo apt-get update
sudo apt-get install grafana


```

Then you start grafana on port 3000:

**Start the server with init.d**  *(MX linux)*

To start the service and verify that the service has started:

```bash
$ sudo service grafana-server start


```

Start the server with systemctl (Raspberry)

```bash
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl status grafana-server
# Configure the Grafana server to start at boot:

sudo systemctl enable grafana-server.service

```



Alternative 2 - install in a Docker container



Log into Grafana : point your browser to **localhost:3000**

First time username/password: admin/admin, and you will be prompted to change the password. *we chose grafana* as password...



It is possible to zoom etc.

## Status monitoring of the Arduinos

The monitoring of the Arduino's is done first as a text interface, later in a GUI

Functions: 

1. View status of all arduino's - when was the last update from this arduino? Which software is run? 

2. Set target temperature for each individual hot-callus-pipe
