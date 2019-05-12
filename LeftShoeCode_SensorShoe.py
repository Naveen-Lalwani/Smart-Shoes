'''
Final Project: Smart Shoes

17-722: Building User Focused Sensor Systems

This file is to be implemented in the left shoe which has all the sensors on it
to sense the heart beat and to count the number of steps and to sense the
command that user wants to do to GUI interface and then to finally send all the
data to the right shoe via Bluetooth.

Authors: Naveen Lalwani, Rangeesh Muthaiyan
Andrew ID: naveenl@andrew.cmu.edu, rmuthaiy@andrew.cmu.edu
''' 
from bluetooth import *
import sys
from pulsesensor import Pulsesensor
import time
from MCP3008 import MCP3008
import Adafruit_MPR121.MPR121 as MPR121

'''
BLUETOOTH CONNECTION ESTABLISHMNET
'''
addr = "B8:27:EB:AF:47:1A"

'''
CUSTOM CHANNEL
'''
if len(sys.argv) < 2:
    print ("No device specified.  Searching all nearby bluetooth devices for")
    print ("the SampleServer service")
else:
    addr = sys.argv[1]
    print ("Searching for SampleServer on %s" % addr)

'''
DEFAULT CHANNEL
'''
# Search for the SampleServer service
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
service_matches = find_service( uuid = uuid, address = addr )

'''
Reconnect if no Connection.
'''
if len(service_matches) == 0:
    print ("Reconnecting...."),
    
while len(service_matches) == 0:
    print (".")
    time.sleep(1)
    service_matches = find_service( uuid = uuid, address = addr )
    
    
first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print ("connecting to \"%s\" on %s" % (name, host))

# Create the client socket
sock = BluetoothSocket( RFCOMM )
sock.connect((host, port))

print ("CONNECTED")
'''
BLUETOOTH CONNECTION ESTABLISHED
'''


'''
Setup
'''
threshold = 1015        # Threshold value for pressure to count for step.
step = 0                # Global step count
state = "STANDING"      # Global User State
cap = MPR121.MPR121()   # Initiating Capacitive Touch
cap.begin()
p = Pulsesensor()       # Initiating Heart Rate Sensor
p.startAsyncBPM()

'''
LOOP
'''
while True:
    # Flag for Developer
	print("Loop Begins")
    
	adc = MCP3008(0, 0)
	
    # Channel 1 for velostat reading. 
    velostat = adc.read(1)
    
    # Count the number of steps and the find the state.
	if (velostat < threshold):
		time.sleep(0.2)
		velostat = adc.read(1)
		if (velostat > threshold):
			step += 1
		else:
			state = "SITTING"
	else:
		time.sleep(0.2)
		velostat = adc.read(1)
		if (velostat > threshold):
			state = "STANDING"
	
    # Capacitive Touch 1: Heart Rate Monitor GUI
	if cap.is_touched(1):
		sendString = "HEART"
		sock.send(sendString)
        
        # Flag for the developer
		print ("0 touched")
        time.sleep(1)
		
        x = 0       # Variable to count for 10 readings
		store = 0   # Variable to store the heart beat
 		try:
			while (x < 10):
				bpm = p.BPM
				if bpm > 50 and bpm < 195:
					store = store + bpm
					print(store)
					x = x + 1
				time.sleep(0.2)
		except:
			p.stopAsyncBPM()
            
        # Take average of the 10 readings.
		store = store / 10
        
        # Send Heart Beat to the right shoe.
		sendString = str(store)
		sock.send(sendString)
	
    # Capacitive Touch 2: Step Counter GUI
	if cap.is_touched(2):
        # Send data collected from global steps and state variable to the right 
        # shoe
		sendString = "STEPS"
		sock.send(sendString)
		time.sleep(1)
		sock.send(str(step))
		time.sleep(1)
		sock.send(state)
		time.sleep(1)
		
    # Capacitive Touch 3: Exit GUI    
	if cap.is_touched(3):
		# Send EXIT command to the GUI
		sendString = "EXIT"
		sock.send(sendString)

# Close the connection.        
sock.close()
