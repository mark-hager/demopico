# Building a Custom Measurement

Here we discuss how to build a custom Measurement component for ScopeFoundry.

We will be describing how to build the `pico_datalog` measurement that is part of the [`demopico`](http://github.com/ScopeFoundry/demopico/) tutorial package.

## Basic Structure

A ScopeFoundry Measurement is defined as a sub-class of `ScopeFoundry.Measurement` with a few methods (functions) defined that will describe how to setup up the measurement's data structures (`setup()`) and user interface (`setup_figure()`) as well as functions to define the Measurement procedure (`run()`) and display (`update_display()`). We will expand on each of these functions in the next few sections.


```python
from ScopeFoundry import Measurement

# Our measurement inherits from the ScopeFoundry Measurement class
class DemoPicoDataLogMeasurement(Measurement):
    
    # this is the name of the measurement that ScopeFoundry uses 
    # when displaying your measurement and saving data related to it    
    name = "pico_datalog"
    
    def setup(self):
        """
        Runs once during App initialization.
        This is the place to load a user interface file,
        define settings, and set up data structures. 
        """

    def setup_figure(self):
        """
        Runs once during App initialization, after setup()
        This is the place to make all graphical interface initializations,
        build plots, etc.
        """
    
    def run(self):
        """
        Runs when measurement is started. Runs in a separate thread from GUI.
        It should not update the graphical interface directly, and should only
        focus on data acquisition.
        """
        
    def update_display(self):
        """
        Displays (plots) the data
        This function runs repeatedly and automatically during the measurement run.
        its update frequency is defined by self.display_update_period
        """
```        

We add this Measurement to our MicroscopeApp by the app's `add_measurement()` method:

```python
class DemoPicoApp(BaseMicroscopeApp):
    name = 'demo_pico_app'

    def setup(self):
        ...
        from demo_pico_datalog_measure import DemoPicoDataLogMeasurement
        self.add_measurement(DemoPicoDataLogMeasurement(app=self))
        ...
```

## Measurement Settings

We need parameters to control how the measurement is performed. These are captured in ScopeFoundry `LoggedQuantity` objects that we add in the measurement's `setup()` function:

```python
    def setup(self):
        # Define the logged quantities
        self.settings.New("log_interval", dtype=float, initial=1.0, unit='s')
        self.settings.New("log_duration", dtype=float, initial=10.0, unit='s')

        self.add_operation("Setup Plot", self.setup_plot)
```


## Run()

This is where the measurement happens!

```python
    def run(self):
        # Get reference to the hardware component
        hw = self.app.hardware['demo_pico']

        # Create a data file to store the log
        # Use the default app file save location and file naming convention
        self.h5f = h5_io.h5_base_file(self.app, measurement=self)
        self.h5_meas_group = h5_io.h5_create_measurement_group(self, self.h5f)
        
        try:
            # Add data array to the H5 file
            self.pr_data = self.h5_meas_group.create_dataset("pr_data", (0,2), maxshape=(None,2))

            start_time = time.monotonic()
            elapsed_time = 0

            while not self.interrupt_measurement_called and elapsed_time < self.settings['log_duration']:
                current_time = time.monotonic()
                elapsed_time = current_time - start_time

                self.settings['progress'] = 100*elapsed_time/self.settings['log_duration']

                # Read the 'pr' setting from the hardware
                pr_value = hw.settings.pr.read_from_hardware()

                # Log the data
                new_data = [elapsed_time, pr_value]
                self.pr_data.resize(self.pr_data.shape[0]+1, axis=0)
                self.pr_data[-1, :] = new_data

                # Sleep for the log interval
                time.sleep(self.settings['log_interval'])

        finally:
            # Close the HDF5 file
            self.h5f.close()
```

### Define measurement steps

### Saving data to disk

Data files are saved as HDF5 files. The `h5_io` subpackage gives us a bunch of helper functions to make this possible

### Interrupting a measurement

The user can interrupt a measurement at anytime. The `run()` function should be able 

## Build a user interface


![Qt Creator Interface](qt-creator-screenshot.png)


### Load ui in setup()
 loading to `setup()`

## Bringing user interface to life

`setup_figure()` and `update_display()`

### Connect graphical widgets to code

```python
    def setup_figure(self):
        ...
        # connect ui widgets to measurement/hardware settings or functions
        self.ui.start_pushButton.clicked.connect(self.start)
        self.ui.interrupt_pushButton.clicked.connect(self.interrupt)
        self.settings.save_h5.connect_to_widget(self.ui.save_h5_checkBox)
        self.func_gen.settings.amplitude.connect_to_widget(self.ui.amp_doubleSpinBox)
        ...
```

### Create PyQtGraph plots

```python
    def setup_figure(self):
        ...        
        # Set up pyqtgraph graph_layout in the UI
        self.graph_layout=pg.GraphicsLayoutWidget()
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)

        # Create PlotItem object (a set of axes)  
        self.plot = self.graph_layout.addPlot(title="Sine Wave Readout Plot")
        # Create PlotDataItem object ( a scatter plot on the axes )
        self.optimize_plot_line = self.plot.plot([0])        
        ...
```

### Update plots during run()

In order to see the data as it is aquired, an `update_display()` function is called repeatedly at an interval defined by `self.display_update_period` (in seconds). This value is set by default to 0.1 seconds, but can be updated in `setup_figure()`. 

Since we created all the plot objects during `setup_figure()` this `update_display()` function can be quite simple. Here we update the `optimze_plot_line` using the data in `self.buffer`, which is being filled by the Measurement `run()` thread.


```python
    def update_display(self):
        self.optimize_plot_line.setData(self.buffer) 
```

## Interacting with Measurement