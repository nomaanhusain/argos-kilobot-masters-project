import os
import pandas as pd

# Directory containing all the subfolders
base_directory = 'output_data/'

# Initialize a dictionary to store results
results = {}

# Loop through each subfolder
for subfolder in os.listdir(base_directory):
    subfolder_path = os.path.join(base_directory, subfolder)

    # Check if it's a directory
    if os.path.isdir(subfolder_path):

        # Read metadata.txt to get the parameters
        metadata_file = os.path.join(subfolder_path, 'metadata.txt')
        with open(metadata_file, 'r') as file:
            metadata = {}
            for line in file:
                key, value = line.strip().split(': ')
                metadata[key] = float(value)

        # Create a tuple key from the relevant parameters
        parameters_key = (metadata['informed_ratio'], metadata['personal_info_weight'], metadata['communication_noise'])

        # Initialize a list to store swarm_quality values from all runs
        swarm_qualities = []

        # Loop through all output_runX.txt files
        for run_file in os.listdir(subfolder_path):
            if run_file.startswith('output_run') and run_file.endswith('.txt'):
                run_file_path = os.path.join(subfolder_path, run_file)

                # Read the swarm_quality column from the run file
                run_data = pd.read_csv(run_file_path, sep='\t')
                swarm_qualities.extend(run_data['swarm_quality'])

        # Calculate the average swarm_quality
        average_swarm_quality = sum(swarm_qualities) / len(swarm_qualities)

        # Store the result keyed by the parameters
        results[parameters_key] = average_swarm_quality

# Convert results to a DataFrame for easier manipulation later
results_df = pd.DataFrame(results.items(), columns=['Parameters', 'Average_Swarm_Quality'])

# Optionally, save the results to a CSV file
results_df.to_csv('best_ir_data/swarm_quality_sn0.8_results.csv', index=False)

print("Processing complete. Results saved.")
