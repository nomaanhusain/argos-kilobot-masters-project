import os
import pandas as pd
import matplotlib.pyplot as plt

# Set the base path to the folders containing the accumulated data
ir=0.8
base_path = f'multiple_run_data/ir{ir}_w0.4_cn0.4/'
# runs = ['run_1/','run_2/', 'run_3/']
runs = ['run_1/', 'run_2/', 'run_3/', 'run_4/', 'run_5/', 'run_6/', 'run_7/', 'run_8/', 'run_9/', 'run_10/', 
        'run_11/', 'run_12/', 'run_13/', 'run_14/', 'run_15/']
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

# Plot the average data
plt.figure(figsize=(10, 6))
color_map = {1: 'red', 2: 'blue', 3: 'green', 4: 'purple', 5: 'yellow'}
# Plot each color as a separate line on the graph
for color in average_df.columns[1:]:  # Skip 'timestep' which is in the first column
    color_id = int(color[6:])
    plt.plot(average_df['timestep'], average_df[color], label=color,color = color_map[color_id])

plt.xlabel('Timestep')
plt.ylabel('Average Number of Robots Committed')
plt.ylim(0,100)
plt.title(f'Number of Robots Committed to Each Color Over Time. IR:{ir}')
plt.legend()
plt.grid(True)
plt.show()
