from ScopeFoundry import Measurement
from ScopeFoundry import h5_io
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
import time
import pyqtgraph as pg

class DemoPicoDataLogMeasurement(Measurement):

    name = "pico_datalog"

    def setup(self):
        # Define the logged quantities
        self.settings.New("log_interval", dtype=float, initial=1.0, unit='s')
        self.settings.New("log_duration", dtype=float, initial=10.0, unit='s')

        self.add_operation("Setup Plot", self.setup_plot)

    def setup_figure(self):
        # You can set up any live plotting or user interface here if needed
        self.ui = load_qt_ui_file(sibling_path(__file__,'demo_pico_datalog_measure.ui'))

        self.ui.start_pushButton.clicked.connect(self.start)
        self.ui.interrupt_pushButton.clicked.connect(self.interrupt)

        self.settings.log_interval.connect_to_widget(self.ui.log_interval_doubleSpinBox)
        self.settings.log_duration.connect_to_widget(self.ui.log_duration_doubleSpinBox)

        self.settings.progress.connect_to_widget(self.ui.progressBar)

        hw = self.app.hardware['demo_pico']
        hw.settings.connected.connect_to_widget(self.ui.pico_connect_checkBox)
        hw.settings.sim.connect_to_widget(self.ui.sim_checkBox)
        hw.settings.led_blink_on.connect_to_widget(self.ui.led_blink_on_checkBox)
        hw.settings.led_blink_freq.connect_to_widget(self.ui.led_blink_freq_doubleSpinBox)
        hw.settings.led_blink_duty.connect_to_widget(self.ui.led_blink_duty_doubleSpinBox)
        hw.settings.pr.connect_to_widget(self.ui.pr_value_doubleSpinBox)

        # Plotting
        self.plot = pg.PlotWidget()
        self.ui.plot_groupBox.layout().addWidget(self.plot)
        self.setup_plot()


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


    def setup_plot(self):
        self.plot.clear()

        self.plot_line = self.plot.plot([1,2,3,4,1,6])

    def update_display(self):
        # Update any GUI elements if needed
        if self.h5f.id.valid: # only read data if file is still open
            self.plot_line.setData(self.pr_data[:,0], self.pr_data[:,1] )
