import json
import matplotlib.pyplot as plt

# List of JSON files
base_path='multiple_run_data/'
file_name='average_accuracy.json'
json_files = [base_path+'ir1.0_w0.6_cn0.2_sn0.5/'+file_name, base_path+'ir0.8_w0.6_cn0.2_sn0.5/'+file_name, 
              base_path+'ir0.6_w0.6_cn0.2_sn0.5/'+file_name]
ir_vals = [1.0,0.8,0.6]
accuracies = []
def load_json_data(file):
    with open(file, 'r') as f:
        data = json.load(f)
    return data

def plot_json_data(json_files):
    plt.figure(figsize=(10, 6))

    # Loop over each JSON file
    for file in json_files:
        # Load the data from JSON
        data = load_json_data(file)
        
        # Extract timesteps and accuracy over time
        # timesteps = data['timesteps']
        # accuracy_over_time = data['accuracy_over_time']
        accuracies.append(data['summary_value'])


    plt.plot(ir_vals, accuracies, marker='o' ,label=r'$\phi_{averaged}$')
    for i, value in enumerate(accuracies):
        plt.text(ir_vals[i], accuracies[i]+0.007, f'{value:.4f}', ha='center', va='top',fontsize=22)
    # Label the plot
    plt.xlabel(r'$\rho$',fontsize=15)
    plt.ylim(0.48,0.58)
    plt.xticks([0.6,0.8,1.0],fontsize=14)
    plt.ylabel(r'$\phi_{averaged}$',fontsize=15)
    plt.yticks(fontsize=14)
    plt.title(r'$\omega=0.6$ $\eta=0.2$ $\zeta=0.5$',fontsize=14)
    plt.legend()
    
    # Show the plot
    plt.grid(True)
    plt.show()

# Call the function to plot the data
plot_json_data(json_files)
