import os
import json
# Function to calculate noise for each robot
def calculate_robot_noise(file_path, correct_color=1):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    
    correct_count = 0
    total_count = 0
    if(len(lines)==0 or lines == None):
        # print(file_path)
        return -1
    for line in lines:
        timestep, color = map(int, line.strip().split())
        if color != 0:  # Ignoring outliers (color 0)
            total_count += 1
            if color == correct_color:
                correct_count += 1
    
    if total_count == 0:
        return -1  # later filter out -1 cases
    

    noise_ratio = 1 - (correct_count / total_count)
    if "20" in file_path:
        print(file_path)
        print(f"total_count:{total_count}, correct_count:{correct_count}, noise_ratio: {noise_ratio}")
    return noise_ratio

# Function to analyze all robot files in a directory
def analyze_robot_data(folder_path, correct_color):
    noise_data = {}
    file_list = [f for f in os.listdir(folder_path) if f.endswith('_sensor.txt')]
    
    for file_name in file_list:
        robot_id = int(file_name.split('_')[1])
        file_path = os.path.join(folder_path, file_name)
        noise_ratio = calculate_robot_noise(file_path, correct_color)
        noise_data[robot_id] = noise_ratio
    noise_data = {x:y for x,y in noise_data.items() if y!=-1}
    # Calculate overall system noise
    system_noise = sum(noise_data.values()) / len(noise_data)
    
    return noise_data, system_noise


# Function to save the noise data to a JSON file
def save_noise_data(filename, n_data, s_noise):
    data_to_save = {
        'system_noise': s_noise,
        'noise_data': n_data
    }
    with open(filename, 'w') as f:
        json.dump(data_to_save, f, indent=4)

# Function to load the noise data from a JSON file
def load_noise_data(filename):
    with open(filename, 'r') as f:
        data_loaded = json.load(f)
    
    n_data = data_loaded['noise_data']
    s_noise = data_loaded['system_noise']
    
    return n_data, s_noise

# Example usage
folder_path = 'sensor_color_output/'  # Change this to your folder path
noise_data, system_noise = analyze_robot_data(folder_path, 1)

filename_json_save="system_noise_run15.json"
save_noise_data(filename_json_save,noise_data,system_noise)

# Print the noise data for each robot
print("Noise data for each robot:")
for robot_id, noise_ratio in noise_data.items():
    print(f"Robot {robot_id}: {noise_ratio:.2%} noise")

# Print the overall system noise
print(f"\nOverall system noise: {system_noise:.2%}")
