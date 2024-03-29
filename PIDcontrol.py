#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
UID_IR = "LsN"
UID_PTC= "TQt"
UID_motor = "6EjgEJ"
UID_analog = "MQJ"

global PTC_temperature
global t0
global goal_temp

import cv2
import numpy
import time

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature_ir_v2 import BrickletTemperatureIRV2
from tinkerforge.bricklet_industrial_ptc import BrickletIndustrialPTC
from tinkerforge.brick_dc import BrickDC
from tinkerforge.bricklet_thermal_imaging import BrickletThermalImaging
from tinkerforge.bricklet_industrial_analog_out_v2 import BrickletIndustrialAnalogOutV2

from simple_pid import PID

t0 = time.time()
with open('data/' + str(t0) + '.txt', 'a') as f:
    f.write('time temp control')

# Callback function for object temperature callback
def cb_object_temperature(temperature):
    print("IR Temperature: " + str(temperature/10.0) + " °C")

# Callback function for temperature callback
def cb_temperature(temperature):
    global PTC_temperature
    global t0

    print("PTC Temperature: " + str(temperature/100.0) + " °C") 
    PTC_temperature = temperature/100.0

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
    

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    #ti = BrickletThermalImaging(UID_thermal, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    mode = 2
    if mode == 1:
        goal_temp = 25
    else:
        goal_temp = 32
            
    #setting Kp Kd and KI - 1, 0.1, 0.1 works best for quick convergence
    pid = PID(1, 0.1, 0.1, setpoint = goal_temp)

    dc = BrickDC(UID_motor, ipcon) 
    print("setting up DC")
    dc.set_drive_mode(dc.DRIVE_MODE_DRIVE_COAST)
    dc.set_pwm_frequency(15000) # Use PWM frequency of 10 kHz
    dc.set_acceleration(10000) 
    dc.set_velocity(0)
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
    # Register temperature callback to function cb_temperature
    ptc.register_callback(ptc.CALLBACK_TEMPERATURE, cb_temperature)
    # Set period for temperature callback to 1s (1000ms)
    ptc.set_temperature_callback_configuration(100, False, "x", 0, 0)

    input("Press enter key to exit\n") # Use raw_input() in Python 2

    print("shutting down")
    dc.set_velocity(0) # Stop motor before disabling motor power
    time.sleep(2) # Wait for motor to actually stop: velocity (100 %) / decceleration (50 %/s) = 2 s
    dc.disable() # Disable motor power

    ipcon.disconnect()