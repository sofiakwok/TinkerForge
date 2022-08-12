#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
#UID_IR = "LsN"
UID_PTC= "TQt"
UID_motor = "6EjgEJ"
#UID_analog = "MQJ"

global PTC_temperature
global IR_temperature
global t0
global temp0

import cv2
import numpy
import time
import keyboard

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature_ir_v2 import BrickletTemperatureIRV2
from tinkerforge.bricklet_industrial_ptc import BrickletIndustrialPTC
from tinkerforge.brick_dc import BrickDC
#from tinkerforge.bricklet_industrial_analog_out_v2 import BrickletIndustrialAnalogOutV2

from simple_pid import PID

#creating text file with three variable header for importing into Matlab
t0 = time.time()
with open('data/' + str(t0) + '.txt', 'a') as f:
    f.write('time temp control')

# Callback function for IR camera object temperature
def cb_object_temperature(temperature):
    #print("IR Temperature: " + str(temperature/10.0) + " °C")
    global IR_temperature

    IR_temperature = temperature/10.0

# Callback function for PTC temperature
def cb_temperature(temperature):
    global PTC_temperature

    #print("PTC Temperature: " + str(temperature/100.0) + " °C") 
    PTC_temperature = temperature/100.0

#square wave thermal profile code
def squarewave(heating):
    t = 0

    if heating == -1:
        goal_temperature = 16
        square_1 = -30000
        square_2 = -20000
        square_3 = 2500
    else:
        goal_temperature = 35
        square_1 = 5000
        square_2 = 2500
        square_3 = -20000

    while t < 25:
        #updating elapsed time
        t = time.time() - t0
        print("t: " + str(t))

        PTC_temperature = ptc.get_temperature()/100

        if heating == -1:
            sign = PTC_temperature > goal_temperature
            sign2 = PTC_temperature > temp0
        else:
            sign = PTC_temperature + 3 < goal_temperature
            sign2 = PTC_temperature < temp0

        if t < 5 or (t < 10 and sign):
            control = square_1
        elif t < 15:
            control = square_2
        elif not sign2:
            control = square_3
        else:
            control = 0

        #capping motor output
        if -30000 > control or control > 30000:
            control = 30000 * numpy.sign(control)

        dc.set_velocity(control)

        #writing to text file
        with open('data/' + str(t0) + '.txt', 'a') as f:
            f.write('\n')
            f.write(str(time.time() - t0) + ' ' + str(PTC_temperature) + ' ' + str(control))
            f.close()

        if keyboard.is_pressed("enter"):
            print("ending loop")
            break

#ramp thermal profile code
def ramp(heating):
    t = 0
    global temp0

    if heating == -1:
        ramp_1 = -20000
        ramp_2 = 3000
    else:
        ramp_1 = 3000
        ramp_2 = -30000

    while t < 25:
        #updating time elapsed
        t = time.time() - t0
        print("t: " + str(t))

        PTC_temperature = ptc.get_temperature()/100

        if heating == -1:
            sign = PTC_temperature < temp0
        else:
            sign = PTC_temperature > temp0

        if t < 15:
            control = ramp_1  
        elif t > 15 and sign:
            control = ramp_2
        else: 
            control = 0

        #capping motor output
        if -30000 > control or control > 30000:
            control = 30000 * numpy.sign(control)
        dc.set_velocity(control)

        #writing to text file
        with open('data/' + str(t0) + '.txt', 'a') as f:
            f.write('\n')
            f.write(str(time.time() - t0) + ' ' + str(PTC_temperature) + ' ' + str(control))
            f.close()

        if keyboard.is_pressed("enter"):
            print("ending loop")
            break

#double peak thermal profile code
def peaks(heating):
    t = 0

    if heating == -1:
        goal_temperature = temp0 - 5
        peak_1 = -30000
        peak_2 = 3000
    else:
        goal_temperature = temp0 + 5
        peak_1 = 5000
        peak_2 = -20000

    counter = 0

    while t < 30:
        #updating time elapsed
        t = time.time() - t0
        print("t: " + str(t))

        PTC_temperature = ptc.get_temperature()/100

        '''
        **PTC temperature based control**
        if heating == -1:
            sign = PTC_temperature > goal_temperature
            sign1 = PTC_temperature < temp0
        else:
            sign = PTC_temperature + 5 < goal_temperature
            sign1 = PTC_temperature > temp0

        if sign and t < 20:
            control = peak_1
        elif sign1:
            control = peak_2
        else: 
            control = 0
        '''

        if heating == -1:
            sign = PTC_temperature < temp0
        else:
            sign = PTC_temperature > temp0

        if t < 7.5:
            control = peak_1
        elif t < 11:
            control = peak_2
        elif t < 17.5:
            control = peak_1
        elif sign:
            control = peak_2
        else:
            control = 0

        #capping motor output at 30000
        if -30000 > control or control > 30000:
            control = 30000 * numpy.sign(control)
        dc.set_velocity(control)

        #writing data to text file in data folder
        with open('data/' + str(t0) + '.txt', 'a') as f:
            f.write('\n')
            f.write(str(time.time() - t0) + ' ' + str(PTC_temperature) + ' ' + str(control))
            f.close()

        if keyboard.is_pressed("enter"):
            print("ending loop")
            break

def starting_temp():
    #program to return to starting temperature of Peltier
    global temp0
    global t0

    pid = PID(1, 0.1, 0.1, setpoint = temp0)

    while not (temp0 + 0.1 > PTC_temperature and temp0 - 0.1 < PTC_temperature):
        v = PTC_temperature
        control = pid(v)*1000
        print("control: " + str(control))
        if -30000 > control or control > 30000:
            control = 30000 * numpy.sign(control)
        dc.set_velocity(control)

        with open('data/' + str(t0) + '.txt', 'a') as f:
            f.write('\n')
            f.write(str(time.time() - t0) + ' ' + str(PTC_temperature) + ' ' + str(control))
            f.close()

        if temp0 == PTC_temperature:
            print("temperature reached")
            break
        if keyboard.is_pressed("enter"):
            print("ending loop")
            break

if __name__ == "__main__":
    global temp0

    ipcon = IPConnection() # Create IP connection
    #ti = BrickletThermalImaging(UID_thermal, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    dc = BrickDC(UID_motor, ipcon) 
    dc.set_drive_mode(dc.DRIVE_MODE_DRIVE_COAST)
    dc.set_pwm_frequency(15000) # Use PWM frequency of 10 kHz
    dc.set_acceleration(10000) 
    dc.set_velocity(0)
    dc.enable()

    '''
    tir = BrickletTemperatureIRV2(UID_IR, ipcon) # Create device object
    # Register object temperature callback to function cb_object_temperature
    tir.register_callback(tir.CALLBACK_OBJECT_TEMPERATURE, cb_object_temperature)
    # Set period for object temperature callback to 1s (1000ms)
    tir.set_object_temperature_callback_configuration(2000, True, "x", 0, 0)
    '''

    ptc = BrickletIndustrialPTC(UID_PTC, ipcon) # Create device object
    temp0 = ptc.get_temperature()/100
    #print("inital temperature: " + str(temp0))
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

    '''if heating == 1:
        starting_temp()'''

    print("shutting down")
    dc.set_velocity(0) # Stop motor before disabling motor power
    time.sleep(3) # Wait for motor to actually stop: velocity (100 %) / decceleration (10000) = 3 s
    dc.disable() # Disable motor power

    ipcon.disconnect()