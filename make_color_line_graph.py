import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Set the path to the folder containing the txt files
folder_path = 'robot_color_output/'

# folder_path = 'multiple_run_data/ir0.6_w0.4_cn0.4/run_2/'


# List all files in the folder
files = [f for f in os.listdir(folder_path) if f.startswith("robot_") and f.endswith("_colors.txt")]

# Determine the number of timesteps dynamically by checking the maximum timestep in any file
sample_file = pd.read_csv(os.path.join(folder_path, files[0]), sep=" ", header=None)
max_timesteps = sample_file[0].max()
print("max_timestep = ",max_timesteps)

# Initialize a defaultdict of lists to hold the counts for each color at each timestep
color_counts = defaultdict(lambda: [0] * max_timesteps)

file_count = 0
# Process each file
for file in files:
    print(file)
    file_path = os.path.join(folder_path, file)
    data = pd.read_csv(file_path, sep=" ", header=None)
    data.columns = ["timestep", "colorId"]
    
    for idx, row in data.iterrows():
        timestep = row['timestep'] - 1  # Adjust for 0-based indexing
        colorId = row['colorId']
        color_counts[colorId][timestep] += 1
    file_count+=1
    print(f"{file_count} files processed")


# Plot the data
plt.figure(figsize=(10, 6))
color_map = {1: 'red', 2: 'blue', 3: 'green', 4: 'purple', 5: 'yellow'}

for colorId, counts in color_counts.items():
    plt.plot(range(1, max_timesteps + 1), counts, label=f'Color {colorId}',color = color_map[colorId])

plt.xlabel('Timestep')
plt.ylim(0,100)
plt.ylabel('Number of Robots Committed')
plt.title('Number of Robots Committed to Each Color Over Time')
plt.legend()
plt.grid(True)
plt.savefig("color.png")
plt.show()