import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Set the base path to the folders containing the runs (e.g., run_1, run_2, run_3)
base_path = 'multiple_run_data/ir0.6_w0.4_cn0.4/'
runs = ['run_1/', 'run_2/', 'run_3/']
num_runs = len(runs)

# Initialize a defaultdict of lists to hold the accumulated counts for each color at each timestep
accumulated_counts = defaultdict(lambda: [0] * 100)  # Assuming 100 timesteps initially

# Determine the number of timesteps dynamically from the first run
first_run_path = os.path.join(base_path, runs[0])
first_file = pd.read_csv(os.path.join(first_run_path, os.listdir(first_run_path)[0]), sep=" ", header=None)
max_timesteps = first_file[0].max()

# Update the defaultdict to reflect the actual number of timesteps dynamically
accumulated_counts = defaultdict(lambda: [0] * max_timesteps)

# Iterate over each run folder
for run in runs:
    print("---------------------")
    print("Run",run)
    run_folder_path = os.path.join(base_path, run)
    
    # List all files in the folder (e.g., robot_0_colors.txt, robot_1_colors.txt)
    files = [f for f in os.listdir(run_folder_path) if f.startswith("robot_") and f.endswith("_colors.txt")]
    
    # Initialize a temporary dictionary for the current run
    run_counts = defaultdict(lambda: [0] * max_timesteps)
    file_count = 0
    # Process each file in the current run folder
    for file in files:
        file_path = os.path.join(run_folder_path, file)
        data = pd.read_csv(file_path, sep=" ", header=None)
        data.columns = ["timestep", "colorId"]
        
        for idx, row in data.iterrows():
            timestep = row['timestep'] - 1  # Adjust for 0-based indexing
            colorId = row['colorId']
            run_counts[colorId][timestep] += 1
        file_count += 1
        print(f"{file_count} files processed")
    
    # Accumulate the counts for this run into the overall counts
    for colorId, counts in run_counts.items():
        for timestep in range(max_timesteps):
            accumulated_counts[colorId][timestep] += counts[timestep]

# Calculate the averages by dividing the accumulated counts by the number of runs
average_counts = {colorId: [count / num_runs for count in counts] for colorId, counts in accumulated_counts.items()}

# Plot the average data
plt.figure(figsize=(10, 6))

for colorId, counts in average_counts.items():
    plt.plot(range(1, max_timesteps + 1), counts, label=f'Color {colorId}')

plt.xlabel('Timestep')
plt.ylabel('Average Number of Robots Committed')
plt.title('Average Number of Robots Committed to Each Color Over Time')
plt.legend()
plt.grid(True)
plt.show()
