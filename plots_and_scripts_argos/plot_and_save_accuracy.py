import os
import pandas as pd
import matplotlib.pyplot as plt
import json


# Save accuracy data to a CSV file
def save_accuracy_data(timesteps, acc_over_time, file_name):
    # Create a DataFrame with timesteps and accuracy
    acc_data = pd.DataFrame({
        'Timestep': timesteps,
        'Accuracy': acc_over_time
    })
    
    # Save to a CSV file
    acc_data.to_csv(file_name, index=False)
    print(f"Accuracy data saved to {file_name}")
# Set the base path to the folders containing the accumulated data
ir=1.0
base_path = f'multiple_run_data/ir{ir}_w0.8_cn0.2_sn0.5/'
# runs = ['run_1/', 'run_2/', 'run_3/', 'run_4/', 'run_5/', 'run_6/', 'run_7/', 'run_8/', 'run_9/', 'run_10/']
runs = ['run_1/', 'run_2/', 'run_3/', 'run_4/', 'run_5/', 'run_6/']
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

# Initialize variables for calculating peak accuracy every 40,000 timesteps
timesteps_per_interval = 40000
peak_accuracies = []

# Loop through each timestep and calculate accuracy
for timestep in average_df['timestep']:
    # Determine the correct color based on the current timestep
    interval_index = (timestep - 1) // timesteps_per_interval
    correct_color = f'color_{(interval_index % 5) + 1}'  # Cycles between color_1 to color_5
    
    # Calculate the accuracy for the current timestep
    correct_color_count = average_df.loc[timestep-1, correct_color]
    accuracy = (correct_color_count / total_robots)
    accuracy_over_time.append(accuracy)
    
    # Track peak accuracy within each 40,000 timestep interval
    if timestep % timesteps_per_interval == 0:
        if len(accuracy_over_time) >= timesteps_per_interval:
            peak_accuracies.append(max(accuracy_over_time[-timesteps_per_interval:]))

peak_accuracies = peak_accuracies[1:]
# print(accuracy_over_time)
# Calculate the average peak accuracy
average_peak_accuracy = sum(peak_accuracies) / len(peak_accuracies) if peak_accuracies else 0

# Save the float in a JSON file
with open(base_path+'average_accuracy.json', 'w') as f:
    json.dump({'summary_value': average_peak_accuracy}, f)

save_accuracy_data(average_df['timestep'],accuracy_over_time,base_path+"accuracy_data.csv")
# Plot the accuracy over time
plt.figure(figsize=(10, 6))
plt.plot(average_df['timestep'], accuracy_over_time, label='Swarm Accuracy Over Time')

plt.xlabel('Timestep',fontsize=14)
plt.ylabel(r'Swarm Performance ($\phi$)',fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.title(f'Swarm Performance IR:{ir}\nAveraged Peak Swarm Performance: {average_peak_accuracy:.4f}',fontsize=14)
plt.grid(True)
plt.ylim(0,1)
plt.legend()
plt.show()

# Print the average peak accuracy
print(f"Average Peak Accuracy: {average_peak_accuracy:.2f}%")
