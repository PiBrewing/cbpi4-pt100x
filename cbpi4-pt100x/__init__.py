
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
import RPi.GPIO as GPIO
from cbpi.api import *
from . import max31865
from subprocess import call

logger = logging.getLogger(__name__)


@parameters([Property.Select(label="csPin", options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27], description="GPIO Pin connected to the CS Pin of the MAX31865 - For MISO, MOSI, CLK no choice by default it's PIN 9, 10, 11"),
    Property.Select(label="ResSens", options = [100,1000],description = "Select 100 for PT100 or 1000 for PT1000"),
    Property.Number(label="RefRest", configurable = True, default_value = 4300, description = "Reference Resistor of the MAX31865 board (it's written on the resistor: 430 or 4300,....)"),
    Property.Number(label="offset",configurable = True, default_value = 0, description="Offset for the PT Sensor (Default is 0)"),
    Property.Number(label="ignore_below",configurable = True, default_value = 0, description="Readings below this value will be ignored"),
    Property.Number(label="ignore_above",configurable = True,default_value = 100, description="Readings above this value will be ignored"),
    Property.Select(label="ConfigText", options=["[0xB2] - 3 Wires Manual","[0xD2] - 3 Wires Auto","[0xA2] - 2 or 4 Wires Manual","[0xC2] - 2 or 4 Wires Auto"], description="Choose beetween 2, 3 or 4 wire PT100 & the Conversion mode at 60 Hz beetween Manual or Continuous Auto"),
    Property.Select(label="Interval", options=[1,5,10,30,60], description="Interval in Seconds")])

		#
		# Config Register
		# ---------------
		# bit 7: Vbias -> 1 (ON), 0 (OFF)
		# bit 6: Conversion Mode -> 0 (MANUAL), 1 (AUTO) !!don't change the noch fequency 60Hz when auto
		# bit5: 1-shot ->1 (ON)
		# bit4: 3-wire select -> 1 (3 wires config), 0 (2 or 4 wires)
		# bits 3-2: fault detection cycle -> 0 (none)
		# bit 1: fault status clear -> 1 (clear any fault)
		# bit 0: 50/60 Hz filter select -> 0 (60Hz - Faster converson), 1 (50Hz)
		#
		# 0b10110010 = 0xB2     (Manual conversion, 3 wires at 60Hz)
		# 0b10100010 = 0xA2     (Manual conversion, 2 or 4 wires at 60Hz)
		# 0b11010010 = 0xD2     (Continuous auto conversion, 3 wires at 60 Hz) 
		# 0b11000010 = 0xC2     (Continuous auto conversion, 2 or 4 wires at 60 Hz) 
		#

class CustomSensor(CBPiSensor):

    def __init__(self, cbpi, id, props):
        super(CustomSensor, self).__init__(cbpi, id, props)
        self.value = 0
        self.value_old = 0
        self.misoPin = 9
        self.mosiPin = 10
        self.clkPin  = 11

        self.csPin = int(self.props.get("csPin"))
        self.ResSens = int(self.props.get("ResSens",1000))
        self.RefRest = int(self.props.get("RefRest",4300))
        self.offset = float(self.props.get("offset",0))
        self.low_filter = float(self.props.get("ignore_below",0))
        self.high_filter = float(self.props.get("ignore_above",100))
        self.ConfigReg = self.props.get("ConfigText")[1:5]
        self.Interval = int(self.props.get("Interval",5))
 
        self.max = max31865.max31865(self.csPin,self.misoPin, self.mosiPin, self.clkPin, self.ResSens, self.RefRest, int(self.ConfigReg,16))
               
    async def run(self):

        while self.running == True:
            # get current Unit setting for temperature (Sensor needs to be saved again or system restarted for now)
            self.TEMP_UNIT=self.get_config_value("TEMP_UNIT", "C")
            self.value = self.max.readTemp()
            if self.TEMP_UNIT == "C": # Report temp in C if nothing else is selected in settings
                self.value=round((self.value + self.offset),2)
            else: # Report temp in F if unit selected in settings
                self.value=round((9.0 / 5.0 * self.value + 32 + self.offset), 2)

            if self.value < self.low_filter or self.value > self.high_filter:
                self.push_update(self.value_old)
            else:
                self.log_data(self.value)
                self.push_update(self.value)
                self.value_old = self.value
            await asyncio.sleep(self.Interval)
    
    def get_state(self):
        return dict(value=self.value)



def setup(cbpi):
    cbpi.plugin.register("PT100X_Sensor", CustomSensor)
    pass
