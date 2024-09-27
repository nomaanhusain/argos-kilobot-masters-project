import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# List of file paths for different parameter runs
ir1='multiple_run_data/ir1.0_w0.6_cn0.2_sn0.5/accuracy_data.csv'
ir2='multiple_run_data/ir0.8_w0.6_cn0.2_sn0.5/accuracy_data.csv'
ir3='multiple_run_data/ir0.6_w0.6_cn0.2_sn0.5/accuracy_data.csv'
accuracy_files = [ir1,ir2,ir3]
parameter_values = [1, 2, 3]  # These represent the different parameter settings for the runs

def create_3d_surface_plot(accuracy_files, parameter_values):
    # Ensure the parameter values align with the files
    if len(accuracy_files) != len(parameter_values):
        raise ValueError("Number of accuracy files must match the number of parameter values")

    # Initialize lists for storing data
    timesteps = None
    accuracy_data = []

    # Load the CSV data into a list of arrays
    for file in accuracy_files:
        accuracy_df = pd.read_csv(file)
        
        if timesteps is None:
            timesteps = accuracy_df['Timestep'].values  # All files should have the same timesteps
        
        accuracy_data.append(accuracy_df['Accuracy'].values)

    # Convert the list of arrays into a 2D NumPy array for plotting
    # Shape will be (number of parameter values, number of timesteps)
    Z = np.array(accuracy_data)

    # Create meshgrid for X (timesteps) and Y (parameter values)
    X, Y = np.meshgrid(timesteps, parameter_values)

    # Create 3D surface plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the surface
    surface = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')

    # Add labels and title
    ax.set_xlabel('Timestep')
    ax.set_ylabel('Parameter')
    ax.set_zlabel('Accuracy (%)')
    ax.set_title('Swarm Accuracy vs Timestep vs Parameter')

    # Add a color bar for reference
    fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)

    # Show plot
    plt.show()

# Example usage
create_3d_surface_plot(accuracy_files, parameter_values)
