import os
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import scipy.stats as stats

# Function to plot data from a log file with polynomial regression and confidence intervals
# def plot_data_with_regression(log_file):
def plot_data_format1(log_file):
    # Regular expression pattern to extract throttle and load cell values
    pattern = r'Pin \d+ - Set throttle to (\d+) - Load cell (\d+)'
    # pattern = r'^(?=\d\d\d\d\d\d\d\d - \d\d?\d? - \d\d?\d? - \d\d\d\d\d\d\d\d\n)'

    # Lists to store extracted values
    throttle_values = []
    load_cell_values = []

    # Read the log file line by line
    with open(log_file, 'r') as file:
        for line in file:
            # Extract throttle and load cell values using regex
            match = re.search(pattern, line)
            if match:
                throttle_values.append(int(match.group(1)))
                load_cell_values.append(int(match.group(2)))

    # Perform polynomial regression
    x = np.array(throttle_values)
    y = np.array(load_cell_values)
    coeffs = np.polyfit(x, y, 3)  # Adjust the polynomial degree as needed
    poly = np.poly1d(coeffs)
    xp = np.linspace(1100, 2000, 100)  # Create points for plotting the regression line

    # Calculate confidence intervals
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    y_pred = intercept + slope * x
    residual = y - y_pred
    dof = len(x) - 2
    t = 2.0  # 95% confidence interval
    # Calculate t value for 50% confidence interval
    # t = stats.t.ppf(1 - (1 - 0.50) / 2, dof)
    confidence = t * np.std(residual) * np.sqrt(1 / len(x) + (xp - np.mean(x)) ** 2 / np.sum((x - np.mean(x)) ** 2))

    # Plot the data with polynomial regression and confidence intervals
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, marker='o', s=5, label='Data')
    plt.plot(xp, poly(xp), 'r-', label='Polynomial Regression')
    plt.fill_between(xp, poly(xp) - confidence, poly(xp) + confidence, color='gray', alpha=0.3, label='95% Confidence Interval')
    plt.xlabel('Throttle (PWM)')
    plt.ylabel('Load Cell')
    plt.title('Throttle vs Load Cell for {} (Polynomial Regression)'.format(log_file))
    plt.grid(True)
    plt.legend()
    plt.show()

# # Function to plot data from the second format of the input file
# def plot_data_format2(log_file):
#     # Regular expression pattern to match the second format of the input file
#     pattern = r'(?=\d\d\d\d\d\d\d\d - \d\d?\d? - \d\d?\d? - \d\d\d\d\d\d\d\d\n)'

#     # Lists to store extracted values
#     middle_numbers1 = []
#     middle_numbers2 = []

#     # Read the log file line by line
#     with open(log_file, 'r') as file:
#         for line in file:
#             # Extract two middle numbers from each line using regex
#             match = re.search(pattern, line)
#             if match:
#                 numbers = line.split(' - ')
#                 if len(numbers) >= 4:
#                     middle_numbers1.append(int(numbers[1]))
#                     middle_numbers2.append(int(numbers[2]))

#     # Plot the data as scatter plot with smaller markers
#     plt.figure(figsize=(10, 6))
#     plt.scatter(middle_numbers1, middle_numbers2, marker='o', s=5)  # Set the marker size to 5
#     plt.xlabel('Number 1')
#     plt.ylabel('Number 2')
#     plt.title('Number 1 vs Number 2 for {} (Format 2)'.format(log_file))
#     plt.grid(True)
#     plt.show()

# Function to plot data from the second format of the input file (time series)
def plot_data_format2(log_file):
    # Regular expression pattern to match lines with timestamp1, v1, v2, and timestamp2
    line_pattern = r'(?=\d{8} - \d{1,3} - \d{1,3} - \d{8}\n)'
    # Regular expression pattern to extract timestamp1, v1, v2, and timestamp2
    extract_pattern = r'(\d{8}) - (\d{1,3}) - (\d{1,3}) - (\d{8})\n'

    # Lists to store extracted values
    timestamp1_values = []
    timestamp2_values = []
    variable1 = []
    variable2 = []

    # Read the log file line by line
    with open(log_file, 'r') as file:
        for line in file:
            # Check if the line matches the pattern
            if re.match(line_pattern, line):
                # Extract timestamp1, v1, v2, and timestamp2 using regex
                match = re.search(extract_pattern, line)
                if match:
                    timestamp1_values.append(int(match.group(1)))
                    variable1.append(int(match.group(2)))
                    variable2.append(int(match.group(3)))
                    timestamp2_values.append(int(match.group(4)))

    # Plot the data as time series with a second subplot for format 2
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(timestamp2_values, variable2, label='Variable 2')
    ax1.plot(timestamp2_values, variable1, label='Variable 1')
    ax1.set_xlabel('Timestamp')
    ax1.set_ylabel('Value')
    ax1.set_title(f'Time Series Plot for {log_file} (Format 2)')
    ax1.grid(True)
    ax1.legend()

    # Third subplot for comparison plot
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(timestamp1_values, [1 if v2 > v1 else 0 for v1, v2 in zip(variable1, variable2)], color='b', marker='o', linestyle='-')
    ax2.set_xlabel('Timestamp')
    ax2.set_ylabel('Comparison Result')
    ax2.set_title(f'Comparison of V2 and V1 for {log_file} (Format 2)')
    ax2.grid(True)

    ax1.sharex(ax2)

    # Synchronize x-axis zooming
    # def on_xlims_change_ax2(ax):
    #     ax1.set_xlim(ax2.get_xlim())
    # ax2.callbacks.connect('xlim_changed', on_xlims_change_ax2)
    
    # def on_xlims_change_ax1(ax):
    #     ax2.set_xlim(ax1.get_xlim())
    # ax1.callbacks.connect('xlim_changed', on_xlims_change_ax1)
    
    plt.show()

# Function to plot data from the second format of the input file (time series)
def plot_data_format3(log_file):
    # Regular expression pattern to match lines with timestamp1, v1, v2, v3, v4, and timestamp2
    # 4586960,0,0,0,0,4587408
    line_pattern = r'(?=\d{1,4}\,\d{7,8}\,\d{1,3}\,\d{7,8}\,\d{1,3}\,\d{7,8}\,\d{1,3}\,\d{7,8}\,\d{1,3}\n)'
    # Regular expression pattern to extract timestamp1, v1, v2, and timestamp2
    extract_pattern = r'(\d{1,4})\,(\d{7,8})\,(\d{1,3})\,(\d{7,8})\,(\d{1,3})\,(\d{7,8})\,(\d{1,3})\,(\d{7,8})\,(\d{1,3})\n'

    # Lists to store extracted values
    timestamp1_values = []
    timestamp2_values = []
    timestamp3_values = []
    timestamp4_values = []
    variable1 = []
    variable2 = []
    variable3 = []
    variable4 = []
    throttle = []

    # Read the log file line by line
    with open(log_file, 'r') as file:
        for line in file:
            # Check if the line matches the pattern
            if re.match(line_pattern, line):
                # Extract timestamp1, v1, v2, and timestamp2 using regex
                match = re.search(extract_pattern, line)
                if match:
                    throttle.append(int(match.group(1)))
                    timestamp1_values.append(int(match.group(2)))
                    variable1.append(int(match.group(3)))
                    timestamp2_values.append(int(match.group(4)))
                    variable2.append(int(match.group(5)))
                    timestamp3_values.append(int(match.group(6)))
                    variable3.append(int(match.group(7)))
                    timestamp4_values.append(int(match.group(8)))
                    variable4.append(int(match.group(9)))

    # Plot the data as time series with a second subplot for format 2
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(timestamp4_values, variable4, label='Phase White 4', color='black')
    ax1.plot(timestamp3_values, variable3, label='Phase Yellow 3', color='orange')
    ax1.plot(timestamp2_values, variable2, label='Phase Green 2', color='green')
    ax1.plot(timestamp1_values, variable1, label='Neutral 1', color='blue')
    ax1.set_xlabel('Timestamp')
    ax1.set_ylabel('Value')
    ax1.set_title(f'Time Series Plot for {log_file} (Format 3)')
    ax1.grid(True)
    ax1.legend()

    # Third subplot for comparison plot
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(timestamp4_values, [1 if v4 > v1 else 0 for v1, v4 in zip(variable1, variable4)], color='black', marker='o', linestyle='-', alpha=0.5)
    ax2.plot(timestamp2_values, [1 if v2 > v1 else 0 for v1, v2 in zip(variable1, variable2)], color='green', marker='o', linestyle='-', alpha=0.5)
    ax2.plot(timestamp3_values, [1 if v3 > v1 else 0 for v1, v3 in zip(variable1, variable3)], color='orange', marker='o', linestyle='-', alpha=0.5)
    ax2.set_xlabel('Timestamp')
    ax2.set_ylabel('Comparison Result')
    ax2.set_title(f'Comparison of Phases and Neutral for {log_file} (Format 3)')
    ax2.grid(True)

    ax1.sharex(ax2)

    # Synchronize x-axis zooming
    # def on_xlims_change_ax2(ax):
    #     ax1.set_xlim(ax2.get_xlim())
    # ax2.callbacks.connect('xlim_changed', on_xlims_change_ax2)
    
    # def on_xlims_change_ax1(ax):
    #     ax2.set_xlim(ax1.get_xlim())
    # ax1.callbacks.connect('xlim_changed', on_xlims_change_ax1)
    
    plt.show()

# List all *.txt files in the current directory
txt_files = [file for file in os.listdir() if file.endswith('.txt')]

# Print numbered list of files
print("Available log files:")
for idx, file in enumerate(txt_files):
    print(f"{idx + 1}. {file}")

# Ask the user to select a file
selected_file_index = int(input("Enter the number corresponding to the file you want to analyze: ")) - 1

# Check if the input index is valid
if 0 <= selected_file_index < len(txt_files):
    selected_file = txt_files[selected_file_index]
    # Check the format of the selected file and call the appropriate plot function
    if 'format1' in selected_file:
        plot_data_format1(selected_file)
    elif 'format2' in selected_file:
        plot_data_format2(selected_file)
    elif 'format3' in selected_file:
        plot_data_format3(selected_file)
    else:
        print("Unknown file format.")
else:
    print("Invalid input. Please enter a valid number.")
