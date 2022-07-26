#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
UID_IR = "LsN"
UID_PTC= "TQt"
UID_motor = "6EjgEJ"
UID_analog = "MQJ"

global PTC_temperature
global IR_temperature
global t0
global temp0
global mode

import cv2
import numpy
import time
import keyboard

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature_ir_v2 import BrickletTemperatureIRV2
from tinkerforge.bricklet_industrial_ptc import BrickletIndustrialPTC
from tinkerforge.brick_dc import BrickDC
from tinkerforge.bricklet_thermal_imaging import BrickletThermalImaging
from tinkerforge.bricklet_industrial_analog_out_v2 import BrickletIndustrialAnalogOutV2

#creating text file with three variable header for importing into Matlab
t0 = time.time()
with open('data/' + str(t0) + '.txt', 'a') as f:
    f.write('time temp control')

# Callback function for object temperature callback
def cb_object_temperature(temperature):
    #print("IR Temperature: " + str(temperature/10.0) + " °C")
    global IR_temperature

    IR_temperature = temperature/10.0

# Callback function for temperature callback
def cb_temperature(temperature):
    global PTC_temperature

    #print("PTC Temperature: " + str(temperature/100.0) + " °C") 
    PTC_temperature = temperature/100.0

#square wave thermal profile code
def squarewave(heating):
    t = 0

    while t < 25:
        #updating elapsed time
        t = time.time() - t0
        print("t: " + str(t))

        goal_temperature = 25 + 13*heating
        PTC_temperature = ptc.get_temperature()/100

        if t < 5:
            control = 30000*heating
        elif t < 15:
            control = 2300*heating   
        else:
            control = -30000*heating

        #capping motor output
        if -30000 > control or control > 30000:
            control = 30000 * numpy.sign(control)
        dc.set_velocity(control)

        #writing to text file
        with open('data/' + str(t0) + '.txt', 'a') as f:
            f.write('\n')
            f.write(str(time.time() - t0) + ' ' + str(PTC_temperature) + ' ' + str(control))
            f.close()

#ramp thermal profile code
def ramp(heating):
    t = 0

    while t < 25:
        #updating time elapsed
        t = time.time() - t0
        print("t: " + str(t))

        goal_temperature = 25 + 13*heating
        PTC_temperature = ptc.get_temperature()/100

        if t < 15:
            control = 5000*heating  
        else:
            control = -30000*heating

        #capping motor output
        if -30000 > control or control > 30000:
            control = 30000 * numpy.sign(control)
        dc.set_velocity(control)

        #writing to text file
        with open('data/' + str(t0) + '.txt', 'a') as f:
            f.write('\n')
            f.write(str(time.time() - t0) + ' ' + str(PTC_temperature) + ' ' + str(control))
            f.close()

#double peak thermal profile code
def peaks(heating):
    t = 0

    while t < 35:
        #updating time elapsed
        t = time.time() - t0
        print("t: " + str(t))

        goal_temperature = 25 + 13*heating
        PTC_temperature = ptc.get_temperature()/100

        if PTC_temperature + 5*heating < goal_temperature:
            control = 30000
        else:
            control = -30000

        #capping motor output at 30000
        if -30000 > control or control > 30000:
            control = 30000 * numpy.sign(control)
        dc.set_velocity(control)

        #writing data to text file in data folder
        with open('data/' + str(t0) + '.txt', 'a') as f:
            f.write('\n')
            f.write(str(time.time() - t0) + ' ' + str(PTC_temperature) + ' ' + str(control))
            f.close()


if __name__ == "__main__":
    global temp0

    ipcon = IPConnection() # Create IP connection
    #ti = BrickletThermalImaging(UID_thermal, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    dc = BrickDC(UID_motor, ipcon) 
    print("setting up DC")
    dc.set_drive_mode(dc.DRIVE_MODE_DRIVE_COAST)
    dc.set_pwm_frequency(10000) # Use PWM frequency of 10 kHz
    dc.set_acceleration(10000) 
    dc.set_velocity(100)
    dc.enable()

    tir = BrickletTemperatureIRV2(UID_IR, ipcon) # Create device object
    # Register object temperature callback to function cb_object_temperature
    tir.register_callback(tir.CALLBACK_OBJECT_TEMPERATURE, cb_object_temperature)
    # Set period for object temperature callback to 1s (1000ms)
    tir.set_object_temperature_callback_configuration(2000, True, "x", 0, 0)

    iao = BrickletIndustrialAnalogOutV2(UID_analog, ipcon) # Create device object
    iao.set_voltage(5000) #in mV
    iao.set_enabled(True)

    ptc = BrickletIndustrialPTC(UID_PTC, ipcon) # Create device object
    temp0 = ptc.get_temperature()/100
    print("inital temperature: " + str(temp0))
    # Register temperature callback to function cb_temperature
    ptc.register_callback(ptc.CALLBACK_TEMPERATURE, cb_temperature)
    # Set period for temperature callback to 1s (1000ms)
    ptc.set_temperature_callback_configuration(2000, False, "x", 0, 0)

    # 1 = heating, -1 = cooling
    heating = 1
    mode = 2
    if mode == 0:
        squarewave(heating)
    elif mode == 1:
        ramp(heating)
    elif mode == 2:
        peaks(heating)
    else:
        print("no mode")

    print("shutting down")
    dc.set_velocity(0) # Stop motor before disabling motor power
    time.sleep(3) # Wait for motor to actually stop: velocity (100 %) / decceleration (50 %/s) = 2 s
    dc.disable() # Disable motor power

    ipcon.disconnect()