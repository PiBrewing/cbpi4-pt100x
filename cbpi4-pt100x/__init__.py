# -*- coding: utf-8 -*-
import asyncio
import logging
import time
from subprocess import call

import board
import digitalio
from adafruit_max31865 import MAX31865
from cbpi.api import *
from cbpi.api.dataclasses import NotificationAction, NotificationType

logger = logging.getLogger(__name__)


@parameters(
    [
        Property.Select(
            label="csPin",
            options=[
                0,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
            ],
            description="GPIO Pin connected to the CS Pin of the MAX31865 - For MISO, MOSI, CLK no choice by default it's PIN 9, 10, 11",
        ),
        Property.Select(
            label="ResSens",
            options=[100, 1000],
            description="Select 100 for PT100 or 1000 for PT1000",
        ),
        Property.Select(
            label="RefRest",
            options=[430, 4300],
            description="Reference Resistor of the MAX31865 board (430 (PT100) or 4300 ohm (PT1000) depending on your board)",
        ),
        Property.Number(
            label="offset",
            configurable=True,
            default_value=0,
            description="Offset for the PT Sensor (Default is 0)",
        ),
        Property.Number(
            label="ignore_below",
            configurable=True,
            default_value=0,
            description="Readings below this value will be ignored",
        ),
        Property.Number(
            label="ignore_above",
            configurable=True,
            default_value=100,
            description="Readings above this value will be ignored",
        ),
        Property.Number(
            label="ignore_delta",
            configurable=True,
            default_value=1,
            description="Ignore reading if delta between two readings is above this value. Must be positive (0: inactive)",
        ),
        Property.Number(
            label="alpha",
            configurable=True,
            default_value=1,
            description="Calculate Average between 2 values. Must be between 0 and 1. 1 deactivates averaging",
        ),
        Property.Select(
            label="Wires",
            options=[2, 3, 4],
            description="Choose between 2, 3 or 4 wire PT100 / PT1000 connection",
        ),
        Property.Select(
            label="Interval",
            options=[1, 5, 10, 30, 60],
            description="Interval in Seconds",
        ),
        Property.Kettle(
            label="Kettle",
            description="Reduced logging if Kettle is inactive (only Kettle or Fermenter to be selected)",
        ),
        Property.Fermenter(
            label="Fermenter",
            description="Reduced logging in seconds if Fermenter is inactive (only Kettle or Fermenter to be selected)",
        ),
        Property.Number(
            label="ReducedLogging",
            configurable=True,
            description="Reduced logging frequency in seconds if selected Kettle or Fermenter is inactive (default: 60 sec | disabled: 0)",
        ),
    ]
)

class CustomSensor(CBPiSensor):

    def __init__(self, cbpi, id, props):
        super(CustomSensor, self).__init__(cbpi, id, props)
        self.value = 0
        self.temp = 0
        self.value_old = 0
        self.misoPin = 9
        self.mosiPin = 10
        self.clkPin = 11

        self.pins = [
            board.D0,
            board.D1,
            board.D2,
            board.D3,
            board.D4,
            board.D5,
            board.D6,
            board.D7,
            board.D8,
            board.D9,
            board.D10,
            board.D11,
            board.D12,
            board.D13,
            board.D14,
            board.D15,
            board.D16,
            board.D17,
            board.D18,
            board.D19,
            board.D20,
            board.D21,
            board.D22,
            board.D23,
            board.D24,
            board.D25,
            board.D26,
            board.D27,
        ]
        self.csPin = int(self.props.get("csPin", 17))
        try:
            spi = board.SPI()
        except:
            spi = None
        cs = digitalio.DigitalInOut(self.pins[self.csPin])
        self.ResSens = int(self.props.get("ResSens", 1000))
        self.RefRest = int(self.props.get("RefRest", 4300))
        self.offset = float(self.props.get("offset", 0))
        self.low_filter = float(self.props.get("ignore_below", 0))
        self.high_filter = float(self.props.get("ignore_above", 100))
        self.Wires = int(self.props.get("Wires", 2))
        self.Interval = int(self.props.get("Interval", 5))
        self.delta_filter = float(self.props.get("ignore_delta", 0))
        if self.delta_filter < 0:
            self.delta_filter = 0

        self.alpha = float(self.props.get("alpha", 1))
        if self.alpha >= 1 or self.alpha <= 0:
            self.alpha = 1

        self.value_old = 9999
        # defines how often a large delta can be rejected
        self.max_counter = 2
        # counts subsequent rejected values
        self.counter = 0

        self.lastlog = 0
        self.sensor = self.get_sensor(self.id)

        self.reducedfrequency = float(self.props.get("ReducedLogging", 60))
        if self.reducedfrequency < 0:
            self.reducedfrequency = 0

        self.kettleid = self.props.get("Kettle", None)
        self.fermenterid = self.props.get("Fermenter", None)

        self.reducedlogging = True if self.kettleid or self.fermenterid else False

        if self.kettleid is not None and self.fermenterid is not None:
            self.reducedlogging = False
            self.cbpi.notify(
                "OneWire Sensor",
                "Sensor '"
                + str(self.sensor.name)
                + "' cant't have Fermenter and Kettle defined for reduced logging.",
                NotificationType.WARNING,
                action=[NotificationAction("OK", self.Confirm)],
            )

        if (self.reducedfrequency != 0) and (self.Interval >= self.reducedfrequency):
            self.reducedlogging = False
            self.cbpi.notify(
                "OneWire Sensor",
                "Sensor '"
                + str(self.sensor.name)
                + "' has shorter or equal 'reduced logging' compared to regular interval.",
                NotificationType.WARNING,
                action=[NotificationAction("OK", self.Confirm)],
            )

        # self.max = max31865.max31865(self.csPin,self.misoPin, self.mosiPin, self.clkPin, self.ResSens, self.RefRest, int(self.ConfigReg,16))
        if spi is not None:
            self.max = MAX31865(
                spi,
                cs,
                rtd_nominal=self.ResSens,
                ref_resistor=self.RefRest,
                wires=self.Wires,
            )
        else:
            self.cbpi.notify(
                "PT100X Sensor",
                "Sensor '"
                + str(self.sensor.name)
                + "' failed to initialize MAX31865. Please check raspi in config, if SPI is enabled",
                NotificationType.ERROR,
                action=[NotificationAction("OK", self.Confirm)],
            )
            logging.error(
                "Sensor {}: Failed to initialize MAX31865. Please check raspi in config, if SPI is enabled".format(
                    self.sensor.name
                )
            )
            self.max = None

    def read(self):
        # get current Unit setting for temperature (Sensor needs to be saved again or system restarted for now)
        self.TEMP_UNIT = self.get_config_value("TEMP_UNIT", "C")
        # temp = self.max.readTemp()
        if self.max is not None:
            temp = self.max.temperature
        else:
            temp = 0

        if (
            self.TEMP_UNIT == "C"
        ):  # Report temp in C if nothing else is selected in settings
            temp = round((temp + self.offset), 2)
        else:  # Report temp in F if unit selected in settings
            temp = round((9.0 / 5.0 * temp + 32 + self.offset), 2)
        return temp

    async def Confirm(self, **kwargs):
        pass

    async def run(self):
        self.kettle = (
            self.get_kettle(self.kettleid) if self.kettleid is not None else None
        )
        self.fermenter = (
            self.get_fermenter(self.fermenterid)
            if self.fermenterid is not None
            else None
        )

        while self.running == True:
            self.temp = self.read()
            if self.value_old == 9999:
                self.value_old = self.temp

            if self.temp < self.low_filter or self.temp > self.high_filter:
                self.temp = self.value_old
            ## 0 deactivates delta Filter
            if self.delta_filter == 0:
                self.counter = 0
                self.value = round(
                    (self.temp * self.alpha + self.value_old * (1 - self.alpha)), 2
                )
                self.value_old = self.value
                self.push_update(self.value)
                if self.reducedlogging:
                    await self.logvalue()
                else:
                    self.log_data(self.value)
                    self.lastlog = time.time()
            # active delta filter
            else:
                delta = abs(self.temp - self.value_old)
                if delta < self.delta_filter:
                    self.value = round(
                        (self.temp * self.alpha + self.value_old * (1 - self.alpha)), 2
                    )
                    self.push_update(self.value)
                    if self.reducedlogging:
                        await self.logvalue()
                    else:
                        self.log_data(self.value)
                        self.lastlog = time.time()
                    self.value_old = self.value
                    self.counter = 0
                else:
                    logging.warning(
                        "Sensor {}: High Delta temp {}".format(
                            self.sensor.name, self.temp
                        )
                    )
                    if self.counter < self.max_counter:
                        self.value = self.value_old
                        self.push_update(self.value_old)
                        if self.reducedlogging:
                            await self.logvalue(self.value_old)
                        else:
                            self.log_data(self.value_old)
                            self.lastlog = time.time()
                        self.counter += 1
                    else:
                        self.counter = 0
                        self.value = round(
                            (
                                self.temp * self.alpha
                                + self.value_old * (1 - self.alpha)
                            ),
                            2,
                        )
                        self.value_old = self.value
                        self.log_data(self.value)
                        self.push_update(self.value)
                        if self.reducedlogging:
                            await self.logvalue()
                        else:
                            self.log_data(self.value)
                            self.lastlog = time.time()

            await asyncio.sleep(self.Interval)

    async def logvalue(self, value=None):
        currentvalue = self.value if value is None else value
        now = time.time()
        if self.kettle is not None:
            try:
                kettlestatus = self.kettle.instance.state
            except:
                kettlestatus = False
            if kettlestatus:
                self.log_data(currentvalue)
                logging.info("Kettle Active")
                self.lastlog = time.time()
            else:
                logging.info("Kettle Inactive")
                if self.reducedfrequency != 0:
                    if now >= self.lastlog + self.reducedfrequency:
                        self.log_data(currentvalue)
                        self.lastlog = time.time()
                        logging.info("Logged with reduced freqency")
                        pass

        if self.fermenter is not None:
            try:
                fermenterstatus = self.fermenter.instance.state
            except:
                fermenterstatus = False
            if fermenterstatus:
                self.log_data(currentvalue)
                logging.info("Fermenter Active")
                self.lastlog = time.time()
            else:
                logging.info("Fermenter Inactive")
                if self.reducedfrequency != 0:
                    if now >= self.lastlog + self.reducedfrequency:
                        self.log_data(currentvalue)
                        self.lastlog = time.time()
                        logging.info("Logged with reduced freqency")
                        pass

    def get_state(self):
        return dict(value=self.value)


def setup(cbpi):
    cbpi.plugin.register("PT100X_Sensor", CustomSensor)
    pass
