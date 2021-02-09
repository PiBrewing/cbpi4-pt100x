# cbpi-pt100-sensor
PT100 / PT1000 probes using a max31865 chip.  for wiring go to https://github.com/thegreathoe/cbpi-pt100-sensor/ updated 8/2/17

IMPORTANT INFORMATION BEFORE YOU START:
Changed Class from PT100 to PT100X -> an existing PT100 sensor might need to be set up again:

Before starting new install, you need to remove or un-assign - all previous sensors with PT100 plugin.

1) Remove original plugin pt100.
2) install new plugin by cloning git:
cd craftbeerpi3/modules/plugins/
git clone https://github.com/avollkopf/cbpi-pt100-sensor
3) reboot.
4) configure sensors with new 100x.

You may need to clear your browser cache if updating from a previous version!!!!!

You can now select the conversion mode and number of wires on your probe in software.  You will need to select a setting to get the probe working after an update.

If you are updating from a previous version, you will need to set the reference resistors on the craftbeerpi hardware page!  My chip uses a 430 ohm resistor 

Using a max31865 board like: https://learn.adafruit.com/adafruit-max31865-rtd-pt100-amplifier/

**
on your pi use the following GPIO pins.
csPin = 8  *this one can be any GPIO you want, if using multiple probes you change this on each one, but keep the other 3 pins the same*
misoPin = 9
mosiPin = 10
clkPin = 11
**

The code for the request to the max chip is from https://github.com/steve71/MAX31865 so all credit really goes there... i slightly modified the code to work with the new plug-in system on craftbeerpi v3.  you can now change the ref resistor from teh hardware page of the craftbeerpi

Manuel neatened up my origional code and added the ability to select the cs pin.... so the rest of the credit goes there... I just kind of peieced it all together.

7/20/20:: Added PT1000 functionality. This can be selected in the setup of the sensor. Added also parameters such as offset, low and high vaule filter that are comparable to the OneWireSensor plugins. PT1000 (2-wire) is for instance used in the Speidel Braumeister 20 / 50 and can be read out directly with this plugin. There is no need to change the sensor or the thermowell for these devices.

8/2/17:: Pascal has been working on a pretty nice update which allows you to select the number of wires used on your probe in software... you still need to sever traces or solder jumpers on the board!  He has also been added as a contributer

7/2/17:: Verified with Pascal Fouchy that it is working on multiple sensors at once, and i have added the ability to change the reference resistor value from the craftbeerpi hardware page

