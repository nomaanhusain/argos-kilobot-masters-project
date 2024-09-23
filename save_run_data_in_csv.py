import os
import pandas as pd
from collections import defaultdict

# Set the base path to the folders containing the runs
base_path = 'multiple_run_data/ir0.8_w0.6_sn0.5_cn0.2/'
# runs = ['run_1/', 'run_2/', 'run_3/', 'run_4/', 'run_5/', 'run_6/', 'run_7/', 'run_8/', 'run_9/', 'run_10/', 
#         'run_11/', 'run_12/', 'run_13/', 'run_14/', 'run_15/']
# runs = ['run_1/', 'run_2/', 'run_3/', 'run_4/', 'run_5/', 'run_6/', 'run_7/', 'run_8/', 'run_9/', 'run_10/']
runs = ['run_7/', 'run_8/', 'run_9/', 'run_10/']
colors = [1, 2, 3, 4, 5]  # Assuming there are 5 colors (1 to 5)

# Process each run
for run in runs:
    print("-------------")
    print(run)
    run_folder_path = os.path.join(base_path, run)
    
    # List all files in the folder (e.g., robot_0_colors.txt, robot_1_colors.txt)
    files = [f for f in os.listdir(run_folder_path) if f.startswith("robot_") and f.endswith("_colors.txt")]
    
    # Determine the number of timesteps dynamically from the first file
    first_file = pd.read_csv(os.path.join(run_folder_path, files[0]), sep=" ", header=None)
    max_timesteps = first_file[0].max()

    # Initialize a defaultdict of lists to hold the counts for each color at each timestep
    color_counts = defaultdict(lambda: [0] * max_timesteps)
    file_count = 0
    # Process each file in the current run folder
    for file in files:
        file_path = os.path.join(run_folder_path, file)
        data = pd.read_csv(file_path, sep=" ", header=None)
        data.columns = ["timestep", "colorId"]

        for idx, row in data.iterrows():
            timestep = row['timestep'] - 1  # Adjust for 0-based indexing
            colorId = row['colorId']
            color_counts[colorId][timestep] += 1
        file_count += 1
        print(f"{file_count} files processed")
    
    # Save the accumulated data for this run to a CSV file
    output_file = os.path.join(run_folder_path, f'{run[0:5]}_accumulated_data.csv')

    # Create a DataFrame to store the results
    df = pd.DataFrame(index=range(1, max_timesteps + 1))

    # Ensure the color columns are ordered by color ID (1 to 5) and always present
    for colorId in colors:
        df[f'color_{colorId}'] = color_counts[colorId]

    # Save the DataFrame to a CSV file with the timestep as the index
    df.index.name = 'timestep'
    df.to_csv(output_file)

    print(f"Accumulated data for {run} saved to {output_file}")