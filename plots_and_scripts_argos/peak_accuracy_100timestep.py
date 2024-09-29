import os
import pandas as pd
import matplotlib.pyplot as plt

# Set the base path to the folders containing the accumulated data
# Set the base path to the folders containing the accumulated data
base_path = 'multiple_run_data/ir0.8_w0.6_cn0.2_10message/'
runs = ['run_1/', 'run_2/', 'run_3/', 'run_4/', 'run_5/', 'run_6/', 'run_7/', 'run_8/', 'run_9/', 'run_10/']
accumulated_files = [os.path.join(base_path, run, f'{run[0:5]}_accumulated_data.csv') for run in runs]

# Read the accumulated data from each run into a list of DataFrames
dfs = [pd.read_csv(file) for file in accumulated_files]

# Ensure all dataframes are aligned on timesteps
for df in dfs:
    df.set_index('timestep', inplace=True)

# Initialize a DataFrame to store the average values
average_df = dfs[0].copy()

# Calculate the average for each color at each timestep
for color in average_df.columns:
    average_df[color] = sum(df[color] for df in dfs) / len(dfs)

# Reset the index to have 'timestep' as a column again for plotting
average_df.reset_index(inplace=True)

# Number of robots (assuming it's the same for all timesteps)
total_robots = average_df.iloc[0, 1:].sum()

# Initialize a list to store accuracy values over time
accuracy_over_time = []

# Initialize variables for calculating the average accuracy of the last 100 timesteps every 40,000 timesteps
timesteps_per_interval = 40000
last_100_timestep_window = 100
interval_accuracies = []

# Loop through each timestep and calculate accuracy
for timestep in average_df['timestep']:
    # Determine the correct color based on the current timestep
    interval_index = (timestep - 1) // timesteps_per_interval
    correct_color = f'color_{(interval_index % 5) + 1}'  # Cycles between color_1 to color_5
    
    # Calculate the accuracy for the current timestep
    correct_color_count = average_df.loc[timestep-1, correct_color]
    accuracy = (correct_color_count / total_robots) * 100
    accuracy_over_time.append(accuracy)
    
    # If within the last 100 timesteps of the interval, store accuracy for averaging
    if timestep % timesteps_per_interval >= (timesteps_per_interval - last_100_timestep_window) or timestep % timesteps_per_interval == 0:
        interval_accuracies.append(accuracy)

# Group the accuracies into chunks of the last 100 timesteps of each 40,000 timestep interval
average_interval_accuracies = []
for i in range(0, len(interval_accuracies), last_100_timestep_window):
    average_interval_accuracies.append(sum(interval_accuracies[i:i + last_100_timestep_window]) / last_100_timestep_window)

# Calculate the average of all the average interval accuracies
average_peak_accuracy = sum(average_interval_accuracies) / len(average_interval_accuracies) if average_interval_accuracies else 0

# Plot the accuracy over time
plt.figure(figsize=(10, 6))
plt.plot(average_df['timestep'], accuracy_over_time, label='Swarm Accuracy Over Time')

plt.xlabel('Timestep')
plt.ylabel('Accuracy (%)')
plt.title(f'Swarm Accuracy Over Time\nAverage Peak Accuracy Over Last 100 Timesteps: {average_peak_accuracy:.2f}%')
plt.grid(True)
plt.ylim(0,100)
plt.legend()
plt.show()

# Print the average peak accuracy
print(f"Average Peak Accuracy Over Last 100 Timesteps: {average_peak_accuracy:.2f}%")
