import pandas as pd
import matplotlib.pyplot as plt
import glob


def read_data(file_path):
    return pd.read_csv(file_path, sep='\t')


# w = 0.6
# sn = 0.6
# cn = 0.4
w = 0.4
sn = 0.6
cn = 0.4

filepath_1 = f"fixed_sensor_data/ir1.0/sn_fixed_{sn}/output_data/run_mt6000_ac100_mcr_0.7_ir1.0_piw{w}_sn{sn}_cn{cn}_cct1000"
filepath_2 = f"fixed_sensor_data/ir0.6/sn_fixed_{sn}/output_data/run_mt6000_ac100_mcr_0.7_ir0.6_piw{w}_sn{sn}_cn{cn}_cct1000"
filepath_3 = f"fixed_sensor_data/ir0.4/sn_fixed_{sn}/output_data/run_mt6000_ac100_mcr_0.7_ir0.4_piw{w}_sn{sn}_cn{cn}_cct1000"

# Read data from all files
file_paths1 = glob.glob(f'{filepath_1}/output_run*.txt')
data_frames1 = [read_data(file) for file in file_paths1]
# Merge data frames on 'timestep'
merged_data1 = pd.concat(data_frames1).groupby('timestep').mean()

# Read data from all files
file_paths2 = glob.glob(f'{filepath_2}/output_run*.txt')
data_frames2 = [read_data(file) for file in file_paths2]
# Merge data frames on 'timestep'
merged_data2 = pd.concat(data_frames2).groupby('timestep').mean()

# Read data from all files
file_paths3 = glob.glob(f'{filepath_3}/output_run*.txt')
data_frames3 = [read_data(file) for file in file_paths3]
# Merge data frames on 'timestep'
merged_data3 = pd.concat(data_frames3).groupby('timestep').mean()

# self.print_timestep_data()

# Plot averaged swarm_quality over timesteps
plt.figure(figsize=(10, 5))
plt.plot(merged_data1.index, merged_data1['swarm_quality'], linestyle="solid", label=r'$\rho=1.0$')
plt.plot(merged_data2.index, merged_data2['swarm_quality'], linestyle="dashed", label=r'$\rho=0.6$')
plt.plot(merged_data3.index, merged_data3['swarm_quality'], linestyle="dotted", label=r'$\rho=0.4$')
plt.ylim(0.0, 1.0)
plt.xlabel('Timestep',fontsize=15)
plt.ylabel(r'$\phi$',fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=20)
plt.title(r"$\omega$"+f"={w} "+r"$\zeta$"+f"={sn} "+r"$\eta$"+f"={cn}",fontsize=20)
plt.legend(fontsize=14)
plt.grid(True)
# plt.savefig(f'{self.main_file_path}/swarm_quality_graphs.png')
plt.show()
plt.close()

# Plot averaged color_x values over timesteps
plt.figure(figsize=(10, 5))
plt.ylim(0, 100)
color_map = {'color_0': 'red', 'color_1': 'blue', 'color_2': 'green', 'color_3': 'purple', 'color_4': 'orange'}
for color_col in merged_data1.columns:
    if 'color' in color_col:
        plt.plot(merged_data1.index, merged_data1[color_col], linestyle='solid', color=color_map[color_col])

for color_col in merged_data2.columns:
    if 'color' in color_col:
        plt.plot(merged_data2.index, merged_data2[color_col], linestyle='dashed', color=color_map[color_col])

for color_col in merged_data3.columns:
    if 'color' in color_col:
        plt.plot(merged_data3.index, merged_data3[color_col], linestyle='dotted', color=color_map[color_col])

plt.xlabel('Timestep')
plt.ylabel('Number of Robots in Favour')
plt.title(
    f"Averaged Color Values  w:{w} sn:{sn}"
    f" cn:{cn}")
# plt.legend()
plt.grid(True)
# plt.savefig(f'{self.main_file_path}/color_count_graphs.png')
plt.show()
plt.close()
