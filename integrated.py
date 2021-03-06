#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
UID_thermal = "RX3"
UID_IR = "LsN"
UID_PTC= "xyz"
UID_voltage = "dsdds"
UID_motor = "adf"

PTC_temperature = 0

import cv2
import numpy

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature_ir_v2 import BrickletTemperatureIRV2
from tinkerforge.bricklet_thermal_imaging import BrickletThermalImaging
from tinkerforge.bricklet_industrial_ptc import BrickletIndustrialPTC
from tinkerforge.bricklet_industrial_analog_out_v2 import BrickletIndustrialAnalogOutV2
from tinkerforge.bricklet_dc_v2 import BrickletDCV2

# Callback function for high contrast image callback
def cb_high_contrast_image(image):
    # image is an tuple of size 80*60 with a 8 bit grey value for each element
    reshaped_image = numpy.array(image, dtype=numpy.uint8).reshape(60, 80)

    # scale image 8x
    resized_image = cv2.resize(reshaped_image, (640, 480), interpolation=cv2.INTER_CUBIC)

    cv2.imshow('High Contrast Image', resized_image)
    cv2.waitKey(1)

# Callback function for object temperature callback
def cb_object_temperature(temperature):
    print("PTC Temperature: " + str(temperature/10.0) + " °C")
    PTC_temperature = temperature

# Callback function for temperature callback
def cb_temperature(temperature):
    print("IR Temperature: " + str(temperature/100.0) + " °C")

# Use velocity reached callback to control temperature
def cb_velocity_reached(velocity, dc):
    goal_temp = 16 #celsius
    diff = 10*(goal_temp - PTC_temperature)
    print('difference: ' + str(diff))
    dc.set_velocity(diff) # negative speed is cooling (printed side up)
    dc.set_enabled(True) # Enable motor power

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    ti = BrickletThermalImaging(UID_thermal, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    # Register high contrast image callback to function cb_high_contrast_image
    ti.register_callback(ti.CALLBACK_HIGH_CONTRAST_IMAGE, cb_high_contrast_image)
    # Enable high contrast image transfer for callback
    ti.set_image_transfer_config(ti.IMAGE_TRANSFER_CALLBACK_HIGH_CONTRAST_IMAGE)

    '''
    tir = BrickletTemperatureIRV2(UID_IR, ipcon) # Create device object
    # Register object temperature callback to function cb_object_temperature
    tir.register_callback(tir.CALLBACK_OBJECT_TEMPERATURE, cb_object_temperature)
    # Set period for object temperature callback to 1s (1000ms) without a threshold
    tir.set_object_temperature_callback_configuration(1000, False, "x", 0, 0)
    '''

    ptc = BrickletIndustrialPTC(UID_PTC, ipcon) # Create device object
    # Register temperature callback to function cb_temperature
    ptc.register_callback(ptc.CALLBACK_TEMPERATURE, cb_temperature)
    # Set period for temperature callback to 1s (1000ms) without a threshold
    ptc.set_temperature_callback_configuration(1000, False, "x", 0, 0)

    '''
    iao = BrickletIndustrialAnalogOutV2(UID, ipcon) # Create device object
    goal_temp = 37 #celsius
    current_diff = abs((goal_temp - PTC_temperature)*100)
    iao.set_current(current_diff) #in mA
    iao.set_enabled(True)
    '''

    dc = BrickletDCV2(UID_motor, ipcon) # Create device object
    dc.set_drive_mode(dc.DRIVE_MODE_DRIVE_COAST)
    dc.set_pwm_frequency(1000) # Use PWM frequency of 10 kHz
    dc.set_motion(4096,
                  16384) # Slow acceleration (12.5 %/s), fast decceleration (50 %/s) for stopping
    # Register velocity reached callback to function cb_velocity_reached
    dc.register_callback(dc.CALLBACK_VELOCITY_REACHED,
                         lambda x: cb_velocity_reached(x, dc))

    input("Press key to exit\n") # Use raw_input() in Python 2

    dc.set_velocity(0) # Stop motor before disabling motor power
    time.sleep(2) # Wait for motor to actually stop: velocity (100 %) / decceleration (50 %/s) = 2 s
    dc.set_enabled(False) # Disable motor power

    #iao.set_enabled(False)
    ipcon.disconnect()
    cv2.destroyAllWindows()