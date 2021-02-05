# cbpi4-pt100x-sensor

PT100 / PT1000 Plugin for CBPi4

PT100 / PT1000 probes using a max31865 chip.  for wiring go to https://github.com/thegreathoe/cbpi-pt100-sensor/ updated 8/2/17

You can select the conversion mode and number of wires on your probe in software.  You will need to select a setting to get the probe working after an update.

You will need to set the reference resistors on the craftbeerpi hardware page!  My max31865 chip uses a 4,3 kohm resistor for the PT1000. It might be 430 ohm for a PT100 board

Using a max31865 board like: https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/

Installation:
clone repo from git

Follow instructions under #4:
https://craftbeerpi.gitbook.io/craftbeerpi4/development

**
on your pi use the following GPIO pins.
csPin = 8  *this one can be any GPIO you want, if using multiple probes you change this on each one, but keep the other 3 pins the same*
misoPin = 9
mosiPin = 10
clkPin = 11
**

The code for the request to the max chip is from https://github.com/steve71/MAX31865 so all credit really goes there... i slightly modified the code from the craftbeerpi v3 plugin(https://github.com/thegreathoe/cbpi-pt100-sensor) to allow also the usage of tha PT1000 and added some other parameters.



05.02.21: Adpated code to run under cbpi4

Old versions:
CBPi3
7/20/20:: Added PT1000 functionality. This can be selected in the setup of the sensor. Added also parameters such as offset, low and high vaule filter that are comparable to the OneWireSensor plugins. PT1000 (2-wire) is for instance used in the Speidel Braumeister 20 / 50 and can be read out directly with this plugin. There is no need to change the sensor or the thermowell for these devices.

8/2/17:: Pascal has been working on a pretty nice update which allows you to select the number of wires used on your probe in software... you still need to sever traces or solder jumpers on the board!  He has also been added as a contributer

7/2/17:: Verified with Pascal Fouchy that it is working on multiple sensors at once, and i have added the ability to change the reference resistor value from the craftbeerpi hardware page

