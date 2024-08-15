Here is a Python script that plots the data from the HDF5 output generated by the `DemoPicoLoggingMeasurement` class. This script uses the `h5py` library to read the HDF5 file and `matplotlib` to plot the data.

### Script to Plot Data from HDF5 File

1. **Install Required Libraries**:
   Make sure you have `h5py` and `matplotlib` installed. You can install them using pip:
   ```sh
   pip install h5py matplotlib
   ```

2. **Plotting Script**:
   Save the following script to a `.py` file and run it to plot the data from the HDF5 file.

```python
import h5py
import matplotlib.pyplot as plt

def plot_demo_pico_logging_data(h5_file_path):
    # Open the HDF5 file
    with h5py.File(h5_file_path, 'r') as h5f:
        # Navigate to the measurement group
        meas_group = h5f['demo_pico_logging']
        
        # Read the dataset
        pr_data = meas_group['pr_data'][:]
        
        # Extract time and pr values
        time_data = pr_data[:, 0]
        pr_values = pr_data[:, 1]
        
        # Plot the data
        plt.figure()
        plt.plot(time_data, pr_values, marker='o', linestyle='-', color='b', label='PR Value')
        plt.xlabel('Time (s)')
        plt.ylabel('PR Value')
        plt.title('Demo Pico Logging Measurement')
        plt.legend()
        plt.grid(True)
        plt.show()

# Path to the HDF5 file
h5_file_path = 'path/to/your/demo_pico_logging_output.h5'

# Call the function to plot data
plot_demo_pico_logging_data(h5_file_path)
```

### Explanation

1. **Import Libraries**:
   - `h5py` is used to read data from the HDF5 file.
   - `matplotlib.pyplot` is used to create the plot.

2. **Open the HDF5 File**:
   - The script opens the HDF5 file in read mode using `h5py.File`.

3. **Read the Dataset**:
   - The script navigates to the `demo_pico_logging` group in the HDF5 file and reads the `pr_data` dataset.

4. **Extract Data**:
   - Time and PR values are extracted from the dataset. The first column is time, and the second column is PR value.

5. **Plot the Data**:
   - The script creates a plot with time on the x-axis and PR values on the y-axis.
   - The plot includes markers and a line connecting the data points, labels, a title, a legend, and a grid for better readability.

6. **Path to the HDF5 File**:
   - Update the `h5_file_path` variable with the path to your HDF5 file generated by the `DemoPicoLoggingMeasurement`.

### Running the Script

1. Save the script to a file, for example, `plot_demo_pico_logging_data.py`.
2. Run the script from the command line:
   ```sh
   python plot_demo_pico_logging_data.py
   ```

Ensure the path to your HDF5 file is correct. The script will read the data from the HDF5 file and display the plot.