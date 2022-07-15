#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
UID_IR = "LsN"
UID_thermal = "RX3"
UID_PTC= "TMz"
UID_motor = "6EjgEJ"

global PTC_temperature
goal_temp = 16 #room temp: 20

import cv2
import numpy
import time

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature_ir_v2 import BrickletTemperatureIRV2
from tinkerforge.bricklet_industrial_ptc import BrickletIndustrialPTC
from tinkerforge.brick_dc import BrickDC
from tinkerforge.bricklet_thermal_imaging import BrickletThermalImaging

# Callback function for object temperature callback
def cb_object_temperature(temperature):
    print("IR Temperature: " + str(temperature/10.0) + " °C")

# Callback function for temperature callback
def cb_temperature(temperature):
    global PTC_temperature

    #print("PTC Temperature: " + str(temperature/100.0) + " °C") 
    PTC_temperature = temperature/100.0

# Use velocity reached callback to control temperature
def cb_velocity_reached(velocity, dc):
    global PTC_temperature

    goal_temp = 29.0 #celsius
    diff = goal_temp - PTC_temperature 
    motor_command = 6000*numpy.sign(diff) + 200*(diff)
    print('motor command: ' + str(motor_command))
    if -9000 > motor_command or motor_command > 9000:
        motor_command = 8000 * numpy.sign(diff)
    dc.set_velocity(motor_command) # negative speed is cooling (printed side up)

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    ti = BrickletThermalImaging(UID_thermal, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    ptc = BrickletIndustrialPTC(UID_PTC, ipcon) # Create device object
    # Register temperature callback to function cb_temperature
    ptc.register_callback(ptc.CALLBACK_TEMPERATURE, cb_temperature)
    # Set period for temperature callback to 1s (1000ms)
    ptc.set_temperature_callback_configuration(200, False, "x", 0, 0)

    '''
    tir = BrickletTemperatureIRV2(UID_IR, ipcon) # Create device object
    # Register object temperature callback to function cb_object_temperature
    tir.register_callback(tir.CALLBACK_OBJECT_TEMPERATURE, cb_object_temperature)
    # Set period for object temperature callback to 1s (1000ms)
    tir.set_object_temperature_callback_configuration(2000, True, "x", 0, 0)
    '''

    dc = BrickDC(UID_motor, ipcon) 
    print("setting up DC")
    dc.set_drive_mode(dc.DRIVE_MODE_DRIVE_COAST)
    dc.set_pwm_frequency(10000) # Use PWM frequency of 10 kHz
    dc.set_acceleration(1000) 
    dc.set_velocity(5000)
    dc.set_current_velocity_period(200)
    # Register velocity reached callback to function cb_current_velocity
    dc.register_callback(dc.CALLBACK_CURRENT_VELOCITY,
                         lambda x: cb_velocity_reached(x, dc))
    dc.enable()

    input("Press enter key to exit\n") # Use raw_input() in Python 2

    print("shutting down")
    dc.set_velocity(0) # Stop motor before disabling motor power
    time.sleep(2) # Wait for motor to actually stop: velocity (100 %) / decceleration (50 %/s) = 2 s
    dc.disable() # Disable motor power

    ipcon.disconnect()