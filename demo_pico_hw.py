from ScopeFoundry import HardwareComponent
import serial
import time
import random
import math

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
        if not self.settings['sim']:
            self.ser = serial.Serial(self.settings['port'], timeout=1.0)
        if self.settings['sim']:
            self._sim_led_blink_on = True
            self._sim_led_blink_freq = 5.0
            self._sim_led_blink_duty = 50.




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

    def threaded_update(self):
        self.settings.pr.read_from_hardware()
        time.sleep(1.0)


    def disconnect(self):
        """
        Disconnects from the hardware by closing the serial connection 
        and disconnecting the settings from the hardware.
        """
        self.settings.disconnect_all_from_hardware()

        if hasattr(self, 'ser'):
            self.ser.close()
            del self.ser
        

    def ser_ask(self, cmd):
        """
        Sends a command to the Pico device via serial communication
        and returns the response. Raises an IOError if the response 
        indicates an error.
        """
        with self.lock:
            self.ser.write((cmd + "\n").encode())
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

    def read_led_blink_freq(self):
        "Pico will reply like this: `led_blink_freq=5.2`"
        if self.settings['sim']:
            return self._sim_led_blink_freq
        resp = self.ser_ask("led_blink_freq?")
        cmd, val = resp.split("=")
        assert cmd == "led_blink_freq"
        return float(val)

    def read_led_blink_duty(self):
        "Will reply like this: `led_blink_duty=45`"
        if self.settings['sim']:
            return self._sim_led_blink_duty
        resp = self.ser_ask("led_blink_duty?")
        cmd, val = resp.split("=")
        assert cmd == "led_blink_duty"
        return int(val)
    
    def read_pr(self):
        "Will reply like this: `pr.value=28323`"
        if self.settings['sim']:
            return self._sim_pr_value()
        resp = self.ser_ask("pr.value?")
        cmd, val = resp.split("=")
        assert cmd == "pr.value"
        return int(val)
    
    ### Write
    def write_led_blink_on(self, x):
        if self.settings['sim']:
            self._sim_led_blink_on = bool(x)
            return
        x = bool(x)
        resp = self.ser_ask(f"led_blink_on={x}")
        cmd, val = resp.split("=")
        assert cmd == "led_blink_on"
        assert str2bool(val) == x

    def write_led_blink_freq(self, x):
        if self.settings['sim']:
            self._sim_led_blink_freq = float(x)
            return        
        x = float(x)
        resp = self.ser_ask(f"led_blink_freq={x}")
        cmd, val = resp.split("=")
        assert cmd == "led_blink_freq"
        assert float(val) == x
    
    def write_led_blink_duty(self, x):
        if self.settings['sim']:
            self._sim_led_blink_duty = int(x)
            return        
        x = int(x)
        resp = self.ser_ask(f"led_blink_duty={x}")
        cmd, val = resp.split("=")
        assert cmd == "led_blink_duty"
        assert int(val) == x

    def _sim_pr_value(self):
        """
        Simulated Photoresistor value
        """
        now = time.monotonic()
        #print((now - t0) % 1/led_blink_freq < 0.5/led_blink_freq)
        if self._sim_led_blink_on:
            if (now  % (1/self._sim_led_blink_freq)) < (0.01*self._sim_led_blink_duty/self._sim_led_blink_freq):
                add_led_light = 1
            else:
                add_led_light = 0
        else:
            add_led_light = 0
        
        pr_value = random.randint(0,10) + 1000+int(100*math.sin(now/100.)) + 50*add_led_light
        return pr_value

def str2bool(x):
    """
    Converts a string to a boolean value. 
    Returns True if the string is one of ['true', '1', 't', 'y', 'yes'] (case-insensitive),
    otherwise returns False.
    """
    return x.strip().lower() in ['true', '1', 't', 'y', 'yes']
