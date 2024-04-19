import os
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import scipy.stats as stats
from format1 import plot_data_format1
from format2 import plot_data_format2
from format3 import plot_data_format3
from format4 import plot_data_format4
from format5 import plot_data_format5


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
    elif 'format4' in selected_file:
        plot_data_format4(selected_file)
    elif 'format5' in selected_file:
        plot_data_format5(selected_file)
    else:
        print("Unknown file format.")
else:
    print("Invalid input. Please enter a valid number.")
