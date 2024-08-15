"""
Hardware:
    MicroController:    Raspberry Pi Pico W https://www.raspberrypi.com/products/raspberry-pi-pico/
    Firmware: Circuit Python 9.1
    LED: Builtin LED at GP25
    Photoresistor: Model XX connected between pins GPIO27 and Pin28 (GND)
"""
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
pullup_pin.pull = digitalio.Pull.UP

pr = analogio.AnalogIn(board.GP27)

print_freq = 0.1 #Hz

tlast = 0

def str2bool(x):
    return x.lower() in ['true', '1', 't', 'y', 'yes']

while True:
    now = time.monotonic()
    #print((now - t0) % 1/led_blink_freq < 0.5/led_blink_freq)
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
