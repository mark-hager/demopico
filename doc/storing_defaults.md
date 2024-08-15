# Storing and loading default settings

ScopeFoundry Apps have the capability to load and save LoggedQuantity settings so that a user can load a configuration for a specific experiment. A good practice is to store instrument defaults in a `defaults.ini` that is loaded upon instrument software start up and can be reloaded to put the system back to defaults.  

An example `defaults.ini` file looks like this, here it setting the port number for a given hardware component, and setting default parameters for a measurement.

```INI
[hardware/demo_pico]
port = /dev/tty.usbmodem1103

[measurement/pico_datalog]
log_interval = 0.01
```

This file can be loaded automatically on startup by adding a command to the `setup()` function of your App:

```python
class DemoPicoApp(BaseMicroscopeApp):

    name = 'demo_pico_app'

    def setup(self):

        from demo_pico_hw import DemoPicoHW
        self.add_hardware(DemoPicoHW(app=self))

        from demo_pico_datalog_measure import DemoPicoDataLogMeasurement
        self.add_measurement(DemoPicoDataLogMeasurement)

        ##### Load settings from an INI file ####
        self.settings_load_ini("demo_pico_app_defaults.ini")
        #########################################
```