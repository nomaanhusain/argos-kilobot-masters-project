import os
import pandas as pd
import matplotlib.pyplot as plt

# List of file paths for different parameter runs
ir1='multiple_run_data/ir1.0_w0.6_cn0.2_sn0.5/accuracy_data.csv'
ir2='multiple_run_data/ir0.8_w0.6_cn0.2_sn0.5/accuracy_data.csv'
ir3='multiple_run_data/ir0.6_w0.6_cn0.2_sn0.5/accuracy_data.csv'
accuracy_files = [ir1,ir2,ir3]

def plot_combined_accuracy(accuracy_files):
    plt.figure(figsize=(10, 6))

    # Loop through each accuracy file, read data, and plot it
    for file in accuracy_files:
        # Extract the parameter name from the file name for labeling
        param_name = file[18:23]
        ln_style = 'solid'
        print(param_name)
        if(param_name == 'ir1.0'):
            ln_style='solid'
            param_name = r'$\rho=1.0$'
        elif(param_name == 'ir0.8'):
            ln_style='dashed'
            param_name = r'$\rho=0.8$'
        else:
            ln_style='dotted'
            param_name = r'$\rho=0.6$'

        # Read the CSV file
        accuracy_data = pd.read_csv(file)

        # Plot accuracy over time
        plt.plot(accuracy_data['Timestep'], accuracy_data['Accuracy'], label=param_name, linestyle=ln_style)
    
    # Label the axes and add title
    plt.xlabel('Timestep',fontsize=15)
    plt.ylabel(r'Swarm Performance $\phi$',fontsize=15)
    plt.ylim(0.0,1.0)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=20)
    plt.title(r'$\omega=0.6$ $\eta=0.2$ $\zeta=0.5$',fontsize=20)

    # Add a legend to show parameter labels
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.show()

# Example usage
plot_combined_accuracy(accuracy_files)
