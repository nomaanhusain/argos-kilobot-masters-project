import glob
import pandas as pd
import re
import os
import numpy as np
import matplotlib.pyplot as plt

import yaml

ACCURACY_THRESHOLD = 0.95  # If the color changing simulation can reach 95% of peak accuracy we call it good and save the timestep

# Load the configuration file, check the config.yaml file for more information and to change to your needs
with open('config.yaml', 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


def read_data(file_path):
    return pd.read_csv(file_path, sep='\t')


ir = 0.0
dataframe_dict = dict()  #0 index for ir0.0, 1 for ir0.2....
while ir <= 1.0:
    filepath = glob.glob(f"output_data/run_mt*ir{round(ir, 2)}*_*/output_run*.txt")
    dataframe = [read_data(file) for file in filepath]
    # dataframe_list.append(pd.concat(dataframe).groupby('timestep').mean())
    dataframe_dict[round(ir, 2)] = pd.concat(dataframe).groupby('timestep').mean()
    print(f"ir:{ir} done")
    ir += 0.2

# Read accuracy data
pattern = re.compile(r'ir:(\d\.\d+)\nw:(\d\.\d+)\nsn:(\d\.\d+)\ncn:(\d\.\d+)\navg_swarm_quality:(\d\.\d+)')
accuracy_data_directory = "accuracy_data/"
accuracy_data_dict = {}
# Iterate over all files in the directory
for filename in os.listdir(accuracy_data_directory):
    if filename.endswith('.txt'):
        with open(os.path.join(accuracy_data_directory, filename), 'r') as file:
            content = file.read()
            match = pattern.search(content)
            if match:
                ir, w, sn, cn, quality = match.groups()
                ir, w, sn, cn, quality = float(ir), float(w), float(sn), float(cn), float(quality)
                # print(f"filename:{filename}")
                # print(f"ir:{ir}, w:{w}, sn:{sn}, cn:{cn}, quality:{quality}")

                # Use (w, sn, cn) as the key
                key = (w, sn, cn)

                if key not in accuracy_data_dict:
                    accuracy_data_dict[key] = {'ir': [], 'quality': []}

                accuracy_data_dict[key]['ir'].append(ir)
                accuracy_data_dict[key]['quality'].append(quality)

w = 0.4
sn = 0.4
cn = 0.4

key = (w, sn, cn)
peak_accuracy_list = accuracy_data_dict[key][
    'quality']  # At index 0 peak accuracy for ir0.0, at 1 peak accuracy for ir0.2, for this key set ofc
ir_list = accuracy_data_dict[key]['ir']
ir_keyed_accuracy_data_dict = dict()
for i in range(len(peak_accuracy_list)):
    # print(f"ir={ir_list[i]}, peak_accuracy={peak_accuracy_list[i]}")
    ir_keyed_accuracy_data_dict[ir_list[i]] = peak_accuracy_list[i]
print(ir_keyed_accuracy_data_dict)

speed_data_dict = {}
for ir_val, dt_frame in dataframe_dict.items():
    peak_accuracy = ir_keyed_accuracy_data_dict[ir_val] * ACCURACY_THRESHOLD
    print(ir_val, peak_accuracy)

    # List to store convergence timesteps for each environment
    convergence_timesteps = []

    # Calculate the total number of environment changes
    num_changes = len(dt_frame) // config['color_change_timestep']
    # Loop through each environment segment
    for i in range(num_changes):
        if i == 0: continue
        start = i * config['color_change_timestep']
        end = start + config['color_change_timestep']

        # Slice the DataFrame for the current environment
        segment = dt_frame.iloc[start:end]
        # Find the first timestep within this segment where swarm_quality meets or exceeds the desired value
        convergence_index = segment[segment['swarm_quality'] >= peak_accuracy].index.min()
        # print(i,convergence_index, start)

        if pd.notnull(convergence_index):  # Check if the desired quality was reached
            convergence_timesteps.append(convergence_index - start)
    # Calculate the average convergence timestep
    if convergence_timesteps:
        average_convergence = np.mean(convergence_timesteps)
        print(f'Average convergence timestep: {average_convergence}')
        speed_data_dict[ir_val] = average_convergence
    else:
        print('Desired swarm quality was not reached in any environment segment.')
        speed_data_dict[ir_val] = -1.0

print(speed_data_dict)

# Plotting time
# Extract ir_ratio and corresponding values
ir_ratios = list(ir_keyed_accuracy_data_dict.keys())
accuracy_values = list(ir_keyed_accuracy_data_dict.values())
speed_values = list(speed_data_dict.values())

plt.figure(figsize=(10, 8))
# Create the plot with dual y-axes
fig, ax1 = plt.subplots()

# Plot accuracy on the primary y-axis
ax1.set_xlabel(r'Informed Ratio ($\rho$)',fontsize=12)
ax1.set_ylabel(r'Max Swarm Performance ($\phi_{max}$)', color='b',fontsize=15)
ax1.plot(ir_ratios, accuracy_values, color='b', marker='o', label=r'$\phi_{max}$')
ax1.set_ylim([0.0, 1.0])
ax1.tick_params(axis='y', labelcolor='b')
plt.yticks(fontsize=18)
plt.xticks(fontsize=14)
# Create a secondary y-axis for speed
ax2 = ax1.twinx()
ax2.set_ylabel(r'Timestep to Agreement ($\tau$)', color='g')
ax2.plot(ir_ratios, speed_values, color='g', marker='o', label=r'$\tau$')

# Handle the outliers
for i, (ir, speed) in enumerate(speed_data_dict.items()):
    print(f"ir={ir},speed={speed}")
    if speed < 1.0:
        ax2.plot(ir, speed, 'rx', markersize=10)
        # ax2.plot(ir, speed, 'rx', markersize=10, label='Outlier' if i == 0 else "")


# Simulation parameters
params = {
    r"$\omega$": w,
    r"$\zeta$": sn,
    r"$\eta$": cn
}
# Add a text box with parameters
param_text = '\n'.join([f"{key}: {value}" for key, value in params.items()])
plt.text(0.03, 0.95, param_text, transform=ax1.transAxes, fontsize=12,
         verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

# Adding titles and legends
# plt.title('Accuracy and Timestep to Convergence vs Informed Ratio')

# Combine legends from both y-axes
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='best')
plt.grid(True)
plt.yticks(fontsize=13)

plt.savefig(f"output_data/speed_accuracy_w{w}_sn{sn}_cn{cn}.png")
# Show the plot
plt.show()
