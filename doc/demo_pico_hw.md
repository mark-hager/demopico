### Demo Pico Hardware / Firmware documentation

This ScopeFoundry demo hardware is a simple example of a microcontroller that illustrates how you can use serial communication to set output parameters and read in real world analog signals, all for $6. If you don't have the parts you may also simulate this device by skipping to [Simulating the Hardware](#simulating-the-hardware)

![Demo Hardware Photo](demo_pico_parts.jpeg)
#### Hardware Overview


- **Microcontroller**: Raspberry Pi Pico W running CircuitPython 9.1.
- **LED**: Built-in LED connected to GPIO pin 25.
- **Photoresistor**: GL5516 Photoresistor connected between GPIO26 & GPIO27 and GND (Pin28).
- **Serial Communication**: Communicates via USB using the `usb_cdc` module. This appears as a virtual COM port (VCP) on the host computer.

### Communication Protocol

This firmware defines a simple serial communication protocol over USB, allowing the host computer to interact with the Raspberry Pi Pico W. The protocol supports querying and setting various parameters related to the LED blinking and reading the photoresistor value.

#### Serial Interface Configuration
- **USB CDC Data Timeout**: 1.0 second.
- **Baud Rate**: Configured through the `usb_cdc` module (default values).
- **Data Handling**:
  - Data is read via the `usb_cdc.data.readline()` method, which reads a line of input terminated by a newline.
  - Responses are sent back to the host via `usb_cdc.data.write()`.
  - Commands expect a newline character `\n` and responses end with `\n`

#### Commands

The communication protocol supports the following commands:

1. **Reset Command**
   - **Command**: `*RST`
   - **Description**: Resets the communication state (flushes input buffer).
   - **Response**: No direct response.

2. **Query LED Blinking Status**
   - **Command**: `led_blink_on?`
   - **Description**: Queries whether the LED blinking is enabled.
   - **Response**: Returns the current status of `led_blink_on`.
     - Example Response: `led_blink_on=True\n`

3. **Set LED Blinking Status**
   - **Command**: `led_blink_on=<value>`
   - **Description**: Sets the LED blinking status.
   - **Parameters**: `<value>` can be `True`, `False`, `1`, `0`, `t`, `f`, `y`, `n`, `yes`, `no`.
   - **Response**: Returns the updated status of `led_blink_on`.
     - Example Response: `led_blink_on=False\n`

4. **Query LED Blinking Frequency**
   - **Command**: `led_blink_freq?`
   - **Description**: Queries the current frequency of the LED blinking.
   - **Response**: Returns the frequency in Hz.
     - Example Response: `led_blink_freq=1.000\n`

5. **Set LED Blinking Frequency**
   - **Command**: `led_blink_freq=<value>`
   - **Description**: Sets the LED blinking frequency in Hz.
   - **Parameters**: `<value>` should be a floating-point number.
   - **Response**: Returns the updated frequency of `led_blink_freq`.
     - Example Response: `led_blink_freq=2.500\n`

6. **Query LED Blinking Duty Cycle**
   - **Command**: `led_blink_duty?`
   - **Description**: Queries the current duty cycle of the LED blinking.
   - **Response**: Returns the duty cycle as a percentage.
     - Example Response: `led_blink_duty=50\n`

7. **Set LED Blinking Duty Cycle**
   - **Command**: `led_blink_duty=<value>`
   - **Description**: Sets the LED blinking duty cycle as a percentage.
   - **Parameters**: `<value>` should be an integer between 0 and 100.
   - **Response**: Returns the updated duty cycle.
     - Example Response: `led_blink_duty=75\n`

8. **Query Photoresistor Value**
   - **Command**: `pr.value?`
   - **Description**: Queries the current value read from the photoresistor.
   - **Response**: Returns the analog value from the photoresistor.
     - Example Response: `pr.value=32768\n`

9. **Unknown Command Handling**
   - **Behavior**: If an unrecognized command is received, the firmware raises an exception and responds with an error message.
   - **Response**: Returns an error message indicating the unknown command.
     - Example Response: `ERR on cmd [unknown_command]: Unknown CMD`

### Data Exchange Format
- **Commands** are sent as strings ending with a newline character (`\n`).
- **Responses** are strings formatted with the respective variable names and values, also ending with a newline (`\n`).

### Error Handling
- The firmware catches exceptions during command processing and responds with an error message detailing the issue.
- Example Error Response: `ERR on cmd [led_blink_freq=invalid_value]: could not convert string to float: 'invalid_value'`

### Timing and Frequency Control
- **LED Blinking Control**:
  - The LED's on/off state is controlled by a duty cycle and frequency.
  - These parameters determine how often and for how long the LED blinks within each cycle.
  

### Summary
This communication protocol enables simple control and monitoring of the Raspberry Pi Pico W's built-in LED and an external photoresistor through a set of predefined serial commands. It allows for querying and modifying settings such as the LED blinking status, frequency, duty cycle, and reading the analog value from the photoresistor.

### Hardware setup
The following instructions presume you have purchased a Raspberry Pi Pico 
The Raspberry Pi Pico W pinout diagram:

![Pico W Pinout](picow-pinout.svg)


In order to read out the photoresistor's analog signal we need to connect it to the Pico. The fully correct way to do this requires an extra couple of resistors and can be found in many [tutorials](https://www.instructables.com/How-to-use-a-photoresistor-or-photocell-Arduino-Tu/). 

![Pico Photoresistor Connection Diagram](pico_pr_connection_diagram_pullup.png)

#### The Lazy Way

But we are going to be lazy and do this with no extra components and no soldering! We will be abusing the internal pullup resistor on GPIO26 and connecting our photoresistor directly onto the board. This is not a good practice for anything reliable, but will get us started on using this to build our first ScopeFoundry instrument.

Here is the wiring diagram:

![wiring diagram](pico_pr_connection_diagram.png)

Connect one pin of the photoresistor to ground and bend the other to have it loop through both GP26 and GP27. As mentioned, we will configure GP26 as an internal pullup resistor while GP27 will be used to read the analog signal of the photoresistor.


![Photo of the photoresistor connections](pico_pr_connection_photo.jpeg)

### Firmware setup

 - Install CircuitPython on the Raspberry Pi Pico W by copying [adafruit-circuitpython-raspberry_pi_pico-en_US-9.1.1.uf2](https://circuitpython.org/board/raspberry_pi_pico_w/) file to the `RPI-RP2` USB drive. For details follow instructions from [AdaFruit](https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython).

 - Copy firmware to the new CIRCUITPY USB drive that appears. Firmware consists of two files: 1) `boot.py` and 2) `code.py`

#### boot.py 

Sets up data serial port channel needed for ScopeFoundry communication:

```python
import usb_cdc
usb_cdc.enable(console=True, data=True)  # Enable console and data
```

#### code.py
This file contains the code to handle communication to ScopeFoundry over serial port and runs the LED and reads the analog read from the photoresistor.

```python
import board
import digitalio
import analogio
import usb_cdc
import time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


usb_cdc.data.timeout = 1.0


t0 = time.monotonic()

led_blink_on = True
led_blink_freq = 1 #Hz
led_blink_duty = 50 # percent

pullup_pin = digitalio.DigitalInOut(board.GP26)
pullup_pin.pull = digitalio.Pull.UP # setting the internal pullup resistor

pr = analogio.AnalogIn(board.GP27)

print_freq = 0.1 #Hz

tlast = 0

def str2bool(x):
    return x.lower() in ['true', '1', 't', 'y', 'yes']

while True:
    now = time.monotonic()
    if led_blink_on:
        if ((now - t0) % (1/led_blink_freq)) < (0.01*led_blink_duty/led_blink_freq):

            led.value = True
        else:
            led.value = False
    else:
        led.value = False

    if ((now - tlast) > (1/print_freq)):
        print((pr.value ,))
        tlast = now

    if usb_cdc.data.in_waiting >0:
        print("data ready", usb_cdc.data.in_waiting)
        cmd = usb_cdc.data.readline()
        cmd = cmd.decode().strip()
        print(f'{cmd=}')


        try:

            if '*RST' in cmd:
                usb_cdc.data.flush()
            elif cmd == '?':
                #usb_cdc.data.write(b"asdf\n")
                outstr = "{:0.3f},{:0.3f}\n".format(sensor.temperature, sensor.relative_humidity)
                usb_cdc.data.write(outstr.encode())
            elif cmd == 'led_blink_on?':
                outstr = f'{led_blink_on=}\n'
                print(outstr)
                usb_cdc.data.write(outstr.encode())
            elif cmd.startswith('led_blink_on='):
                val = cmd.split('=')[-1]
                led_blink_on = str2bool(val)
                outstr = f'{led_blink_on=}\n'
                print(outstr)
                usb_cdc.data.write(outstr.encode())
            elif cmd == 'led_blink_freq?':
                outstr = f'{led_blink_freq=}\n'
                print(outstr)
                usb_cdc.data.write(outstr.encode())
            elif cmd.startswith('led_blink_freq='):
                val = cmd.split('=')[-1]
                led_blink_freq = float(val)
                outstr = f'{led_blink_freq=}\n'
                print(outstr)
                usb_cdc.data.write(outstr.encode())
            elif cmd == 'led_blink_duty?':
                outstr = f'{led_blink_duty=}\n'
                print(outstr)
                usb_cdc.data.write(outstr.encode())
            elif cmd.startswith('led_blink_duty='):
                val = cmd.split('=')[-1]
                led_blink_duty = abs(int(val))
                outstr = f'{led_blink_duty=}\n'
                print(outstr)
                usb_cdc.data.write(outstr.encode())
            elif cmd == 'pr.value?':
                outstr = f'{pr.value=}\n'
                print(outstr)
                usb_cdc.data.write(outstr.encode())
            else:
                raise ValueError(f"Unknown CMD")
        except Exception as err:
            outstr = f"ERR on cmd [{cmd}]: {err}"
            print(outstr)
            usb_cdc.data.write(outstr.encode())
```
### Simulating the hardware
**TODO**

Next, proceed to the instructions for [building the instrument app](building_instrument_app).