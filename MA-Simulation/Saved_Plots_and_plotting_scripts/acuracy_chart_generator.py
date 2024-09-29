import os
import re
import matplotlib.pyplot as plt

# Initialize a dictionary to store the data grouped by (w, sn, cn)
data = {}

# Directory containing the text files
directory = 'output_data/'  # adjust the path accordingly

# Regex to extract the parameters and avg_swarm_quality
pattern = re.compile(r'ir:(\d\.\d+)\nw:(\d\.\d+)\nsn:(\d\.\d+)\ncn:(\d\.\d+)\navg_swarm_quality:(\d\.\d+)')

# Iterate over all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.txt'):
        with open(os.path.join(directory, filename), 'r') as file:
            content = file.read()
            match = pattern.search(content)
            if match:
                ir, w, sn, cn, quality = match.groups()
                ir, w, sn, cn, quality = float(ir), float(w), float(sn), float(cn), float(quality)
                print(f"filename:{filename}")
                print(f"ir:{ir}, w:{w}, sn:{sn}, cn:{cn}, quality:{quality}")

                # Use (w, sn, cn) as the key
                key = (w, sn, cn)

                if key not in data:
                    data[key] = {'ir': [], 'quality': []}

                data[key]['ir'].append(ir)
                data[key]['quality'].append(quality)

# Now plot the data for each (w, sn, cn) combination
for (w, sn, cn), values in data.items():
    plt.figure()
    plt.plot(values['ir'], values['quality'], marker='o',color = 'purple')
    plt.title(f'Accuracy vs Informed Ratio (w={w}, sn={sn}, cn={cn})')
    plt.xlabel('Informed Ratio')
    plt.ylim(0.0, 1.0)
    plt.ylabel('Accuracy')
    plt.grid(True)
    plot_name=f"output_data/accuracy_w{w}_sn{sn}_cn{cn}.png"
    plt.savefig(plot_name)
    plt.show()
    plt.close()
