import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.stats import linregress
import scipy.stats as stats

# Function to plot data from the third format of the input file (time series)
def plot_data_load_cell(log_file):
    # Regular expression pattern to match lines with timestamp, load_cell
    line_pattern = r'(?=\d{7,12}\,\d{1,4}\n)'
    # Regular expression pattern to extract timestamp, load_cell
    extract_pattern = r'(\d{7,12})\,(\d{1,4})'

    # Lists to store extracted values
    timestamp = []
    load_cell = []

    # Read the log file line by line
    with open(log_file, 'r') as file:
        for line in file:
            # Check if the line matches the pattern
            if re.match(line_pattern, line):
                # Extract timestamp1, v1, v2, and timestamp2 using regex
                match = re.search(extract_pattern, line)
                if match:
                    timestamp.append(int(match.group(1)))
                    load_cell.append(int(match.group(2)))

    timestamp = np.array(timestamp)
    load_cell = np.array(load_cell)
    # # Plot the data as time series, with some serious downsampling/averaging

    scale_x = 1e6
    ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scale_x))

    # Load cell vs time
    # Filter load cell data with a moving average, then downsample it
    # Smoothing the data with a moving average filter
    def moving_average(data, window_size):
        return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

    window_size = 2000  # Adjust this value based on the degree of smoothing desired
    smoothed_load_cell = moving_average(load_cell, window_size)

    # Downsampling the data
    downsample_factor = 2000
    downsampled_timestamp = timestamp[:len(smoothed_load_cell):downsample_factor]
    downsampled_load_cell = smoothed_load_cell[::downsample_factor]

    fig, ax = plt.subplots(figsize=(10, 6))
    # ax.scatter(timestamp, load_cell, marker='o', s=2, label='Data', alpha=0.5)
    # ax.plot(timestamp[:len(smoothed_load_cell)], smoothed_load_cell, label=f'Smoothed (Window Size = {window_size})', linestyle='--')
    ax.scatter(timestamp[:len(smoothed_load_cell)], smoothed_load_cell, label=f'Smoothed (Window Size = {window_size})', s=2)
    ax.plot(downsampled_timestamp, downsampled_load_cell, label=f'Downsampled (Factor = {downsample_factor})', color="orange")
    # ax.plot(downsampled_timestamp, downsampled_load_cell, label=f'Downsampled (Factor = {downsample_factor})', color="blue")
    # ax.plot(xp, poly(xp), 'r-', label='Polynomial Regression')
    # ax.fill_between(xp, poly(xp) - confidence, poly(xp) + confidence, color='gray', alpha=0.3, label='95% Confidence Interval')
    ax.xaxis.set_major_formatter(ticks_x)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Load Cell')
    ax.set_title(f'Load cell over time for {log_file} (SMA = {window_size}, downsampling = {downsample_factor})')
    ax.grid(True)
    ax.legend()
    plt.show()
