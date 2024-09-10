import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# File paths to all runs
files = ['system_noise_run8.json', 'system_noise_run9.json', 'system_noise_run10.json', 'system_noise_run11.json', 'system_noise_run12.json']

# Initialize a list to store all noise data
combined_noise_data = []

# Iterate through all files and aggregate noise data
for file in files:
    with open(file) as f:
        data = json.load(f)
        combined_noise_data.extend(data["noise_data"].values())

# Calculate the mean of the combined noise data
mean_noise = np.mean(combined_noise_data)
print(f"The mean of the combined noise data is: {mean_noise:.4f}")

# Create a DataFrame for easier plotting
df = pd.DataFrame({'Noise': combined_noise_data})
print(combined_noise_data[1:80])
# Create the box plot with individual dots overlaid
plt.figure(figsize=(6, 8))
sns.boxplot(y='Noise', data=df, color='lightblue', width=0.3)
sns.stripplot(y='Noise', data=df, color='black', jitter=True, size=3)

# Add titles and labels
plt.title('Distribution of System Noise', fontsize=12)
plt.ylabel('System Noise Value', fontsize=12)

# Show the plot
plt.tight_layout()
plt.show()
