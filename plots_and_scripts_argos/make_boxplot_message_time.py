import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
# Folder where your text files are stored
folder_path = 'time_output/'

# List to store data for all robots combined
all_times = []

# Dictionary to store data for each robot ID
robot_times = {}

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith("_times.txt"):
        file_path = os.path.join(folder_path, filename)
        
        # Read the file content
        with open(file_path, 'r') as file:
            # Read all lines and convert to floats
            times = [float(line.strip()) for line in file.readlines() if line.strip()]
        
        # Skip empty files
        if times:
            # Add to the overall list
            all_times.extend(times)
            
            # Extract robot ID from filename
            robot_id = filename.split('_')[1]
            robot_times[robot_id] = times

print(f"Average timeteps for 10 messages = {sum(all_times)/len(all_times)}")
df = pd.DataFrame({'Timestep': all_times})
# Generate the first box plot: Combined data from all robots
plt.figure(figsize=(6, 8))
# plt.boxplot(all_times)

sns.boxplot(y='Timestep', data=df, color='lightblue', width=0.3, showfliers=False)
sns.stripplot(y='Timestep', data=df, color='black', jitter=True, size=3)
# plt.title('Box Plot of Time Steps (All Robots Combined)')
plt.title('Distribution of Timesteps for 10 messages', fontsize=12)
plt.ylabel('Timesteps', fontsize=12)
plt.tight_layout()
plt.show()
# plt.ylabel('Time Steps')
# plt.xticks([1], ['All Robots'])
# plt.grid(True)
# plt.show()

# Generate the second box plot: Individual box plots for each robot ID
# plt.figure(figsize=(14, 8))

# # We convert the dictionary into a DataFrame for easier plotting
# robot_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in robot_times.items()]))

# # Plotting the boxplot for each robot ID
# robot_df.boxplot()
# plt.title('Box Plot of Time Steps by Robot ID')
# plt.ylabel('Time Steps')
# plt.xlabel('Robot ID')
# plt.grid(True)
# plt.xticks(rotation=90)
# plt.show()
