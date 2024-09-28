import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


class HeatmapMaker:

    def __init__(self, root_path):
        self.root_path = root_path

    def parse_metadata(self, filepath):
        with open(filepath, 'r') as file:
            metadata = {}
            for line in file:
                key, value = line.strip().split(': ')
                metadata[key] = float(value) if '.' in value else int(value)
        return metadata

    def parse_output_run(self, filepath):
        return pd.read_csv(filepath, delim_whitespace=True)

    def aggregate_swarm_quality(self, df):
        swarm_quality = df[df['timestep'] % 999 == 0]['swarm_quality']
        swarm_quality = swarm_quality[2:]
        return swarm_quality.mean()

    def collect_data(self, root_dir):
        data = []
        for run_dir in os.listdir(root_dir):
            run_path = os.path.join(root_dir, run_dir)
            if os.path.isdir(run_path):
                # print("run_path: ", run_path)
                metadata_path = os.path.join(run_path, 'metadata.txt')
                # print("metadata_path: ", metadata_path)
                metadata = self.parse_metadata(metadata_path)

                swarm_qualities = []
                for output_file in os.listdir(run_path):
                    if output_file.startswith('output_run') and output_file.endswith('.txt'):
                        output_path = os.path.join(run_path, output_file)
                        # print("output_path: ", output_path)
                        output_run = self.parse_output_run(output_path)
                        avg_quality = self.aggregate_swarm_quality(output_run)
                        swarm_qualities.append(avg_quality)

                avg_swarm_quality = np.mean(swarm_qualities)
                # print(f"^ Average swarm quality: {round(avg_swarm_quality,3)}, piw: {metadata['personal_info_weight']}"
                #       f" cn: {metadata['communication_noise']}, sn: {metadata['sensor_noise']}")
                # print("------------------")

                data.append({
                    'personal_info_weight': metadata['personal_info_weight'],
                    'communication_noise': metadata['communication_noise'],
                    'sensor_noise': metadata['sensor_noise'],
                    'swarm_quality': avg_swarm_quality
                })
        return pd.DataFrame(data)

    def plot_heatmap(self, data, x_param, y_param, value_param, title):
        pivot_table = data.pivot_table(values=value_param, index=y_param, columns=x_param)
        pivot_table.to_csv(title + '.csv')
        sns.heatmap(pivot_table, annot=True, cmap='coolwarm')
        plt.title(title)
        plt.savefig(title + '.png')
        plt.show()
        plt.close()

    def execute_heatmaps_creation(self):
        data = self.collect_data(self.root_path)
        self.plot_heatmap(data, 'sensor_noise', 'personal_info_weight', 'swarm_quality',
                          'Personal_Info_Weight_vs_Sensor_Noise')
        self.plot_heatmap(data, 'communication_noise', 'personal_info_weight', 'swarm_quality',
                          'Personal_Info_Weight_vs_Communication_Noise')
        self.plot_heatmap(data, 'sensor_noise', 'communication_noise', 'swarm_quality',
                          'Sensor_Noise_vs_Communication_Noise')
