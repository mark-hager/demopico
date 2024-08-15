# Building a Custom Hardware Plug-in

Here we discuss how to build a custom hardware plug-in for ScopeFoundry. If one is not available in our list of plug-ins, you can build one based on this tutorial. We will do this through 3 sections: Understand the communication protocol required for python to interface to the device, second write a ScopeFoundry `HardwareComponent`, and finally package up the result to share with the ScopeFoundry project and other users.

![diagram](Slide09.png)

## Low-level device interface

Most scientific devices have programmatic ways to communicate to them, either through a vendor-provided API that talks to a device driver, or a communications protocol for a device connected by a standard communication pathway (RS232 serial, Ethernet, modbus etc)

The manufacturer often provides the commands needed for the computer to talk with your hardware. You should find your device's communication protocol within the provided manufacturer documentation, hopefully reverse engineering a communication protocol is not required! For this tutorial we will be communicating to our [Demo Pico microcontroller](demo_pico_hw) over a virtual (USB) serial port. Here are some test commands to illustrate communication with the device:

```python
import serial

with serial.Serial("COM3", timeout=1.0) as ser:
    ser.flush()
    ser.write(b"*RST\n")
    ser.write(b"led_blink_on=1\n")
    print(ser.readline())
    ser.write(b"led_blink_freq=5\n")
    print(ser.readline())    
    #ser.write(b"led_blink_duty=a\n")
    #print(ser.readline())    
    ser.write(b"pr.value?\n")
    print(ser.readline())    
```


The first step to controlling a device with ScopeFoundry is to create a convienient Python wrapper for the device, if one does not yet exist. We often do this by wrapping the hardware functionality that we require in to a python object class. This low-level code is not dependent on ScopeFoundry, and is not required for building a hardware plugin, but illustrates good encapsulation of hardware functionality into a python object.

When we create an instance of this device class, we begin communication to the device. Other methods with names starting with `read_` or `write_` are the messages we can pass back and forth to the device.

```python
    def ser_ask(self, cmd):
        """
        Sends a command to the Pico device via serial communication
        and returns the response. Raises an IOError if the response 
        indicates an error.
        """
        self.ser.write((cmd + "\n").encode())
        #print(ser.readline())
        resp = self.ser.readline().decode()
        if resp.startswith("ERR"):
            raise IOError(resp)
        return resp

    def read_led_blink_on(self):
        "Will reply like this: `led_blink_on=True`"
        if self.settings['sim']:
            return self._sim_led_blink_on
        resp = self.ser_ask("led_blink_on?")
        cmd, val = resp.split("=")
        assert cmd == "led_blink_on"
        return str2bool(val)

    def write_led_blink_on(self, x):
        if self.settings['sim']:
            self._sim_led_blink_on = bool(x)
            return
        x = bool(x)
        resp = self.ser_ask(f"led_blink_on={x}")
        cmd, val = resp.split("=")
        assert cmd == "led_blink_on"
        assert str2bool(val) == x

```




## Hardware Component

The next step is to create the `HardwareComponent` ScopeFoundry plug-in. Here we sub-class `HardwareComponent` and define three methods: `setup()`, `connect()`, and `disconnect()`: 

```python
class DemoPicoHW(HardwareComponent):
    """
    Defines a ScopeFoundry hardware component class DemoPicoHW for interacting 
    with a Pico device via serial communication.
    """

    name = 'demo_pico'
    # A class attribute representing the name of the hardware component shown in UI and data files.

    def setup(self):
        """Defines the hardware settings.
            - port: The serial port to which the Pico device is connected (default is “COM1”).
            - led_blink_on: A boolean indicating whether the LED should blink.
            - led_blink_freq: A float representing the LED blink frequency in Hz.
            - led_blink_duty: An integer representing the LED blink duty cycle as a percentage.
            - pr: An integer representing a the analog read value from the photoresistor.
        """
        self.settings.New("port", dtype=str, initial="COM1") # /dev/tty.usbmodem2103
        self.settings.New("led_blink_on", dtype=bool)
        self.settings.New("led_blink_freq", dtype=float, unit='Hz', si=False)
        self.settings.New("led_blink_duty", dtype=int, unit='%')
        self.settings.New("pr", dtype=int, ro=True)
        self.settings.New('sim', dtype=bool)

    def connect(self):
        """
        Establishes a serial connection to the Pico device and connects
        the settings to their respective read/write functions.
        """
        self.ser = serial.Serial(self.settings['port'], timeout=1.0)

        self.settings.led_blink_on.connect_to_hardware(
            read_func = self.read_led_blink_on,
            write_func = self.write_led_blink_on,
        )

        self.settings.led_blink_freq.connect_to_hardware(
            read_func = self.read_led_blink_freq,
            write_func = self.write_led_blink_freq,
        )

        self.settings.led_blink_duty.connect_to_hardware(
            read_func = self.read_led_blink_duty,
            write_func = self.write_led_blink_duty,
        )
        
        self.settings.pr.connect_to_hardware(
            read_func = self.read_pr,
        )

        # update state from HW
        self.read_from_hardware()
    def disconnect(self):
        """
        Disconnects from the hardware by closing the serial connection 
        and disconnecting the settings from the hardware.
        """
        self.settings.disconnect_all_from_hardware()

        if hasattr(self, 'ser'):
            self.ser.close()
            del self.ser
        
```

There are several critical components contained within this module which essentially handle signals, settings, and links to low level device functions. 

For the sake of simplicity we've omitted hardware level signals in this basic tutorial.

- `class`: We make our module a _subclass_ of `HardwareComponent`.
	- `setup()`
		- Here we set up a few settings for this hardware, these settings are `LoggedQuantity` objects that contain a hardware value that can read or written. This object helps keep this value in sync between hardware, measurement and graphical interface.

	- `connect()`
		- We define an object `self.ser` which instantiates the low-level device wrapper and thereby accesses hardware functions.
		- Using `connect_to_hardware()` we   to the device level `self.read_led_blink_on`. Every time the we call `led_blink_on.read_from_hardware()` is called, the linked functions will be called.
		- We run `self.read_from_hardware()` to update all hardware-connected settings with initial readout values.

	- `disconnect()`
		- We clean up the mess we made by removing objects after use.

By having the `connect()` and `disconnect()`  we can cleanly reconnect hardware during an App run. This is especially useful when debugging a hardware plug-in to a new device. 


## Where to Find Out More

This tutorial code is available in the [demopico](https://github.com/scopefoundry/demopico/) repository.

For source code of all ScopeFoundry projects visit our [GitHub page](https://github.com/scopefoundry/).

