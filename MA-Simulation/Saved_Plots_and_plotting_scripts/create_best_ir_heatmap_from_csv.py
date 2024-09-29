import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Define a custom function to format the annotations
def custom_annotation(val):
    return r"$\rho$"+f":{val}"  # Format the float as rho= with 2 decimal places
    # return "rho="


sn = 0.6
# Load the CSV file saved earlier
results_df = pd.read_csv(f'best_ir_data/swarm_quality_sn{sn}_results.csv')
results_df = results_df.sort_index().sort_index(axis=1)
# Split the Parameters tuple into separate columns for easier manipulation
results_df[['informed_ratio', 'personal_info_weight', 'communication_noise']] = pd.DataFrame(
    results_df['Parameters'].apply(eval).tolist(), index=results_df.index
)

# Group by personal_info_weight and communication_noise, and find the best informed_ratio
best_informed_ratio_df = results_df.loc[
    results_df.groupby(['personal_info_weight', 'communication_noise'])['Average_Swarm_Quality'].idxmax()
]

# Pivot the table so that personal_info_weight is on the y-axis and communication_noise is on the x-axis
pivot_table_ir = best_informed_ratio_df.pivot_table(index='personal_info_weight', columns='communication_noise',
                                                       values='informed_ratio')

# Pivot the table for Average_Swarm_Quality for coloring
pivot_swarm_quality = best_informed_ratio_df.pivot_table(index='personal_info_weight', columns='communication_noise',
                                                         values='Average_Swarm_Quality')

# Count the number of cells with the value 1.0
one_count = (pivot_table_ir == 1.0).sum().sum()
total_cells = pivot_table_ir.size

# Print the count and percentage
print(f"Number of cells with informed_ratio 1.0: {one_count} out of {total_cells} ({(one_count / total_cells) * 100:.2f}%)")

# Plot the map using sns.heatmap, but just with annotations
plt.figure(figsize=(10, 8))
# sns.heatmap(pivot_table_ir, annot=True, fmt='.2f', cmap='viridis', cbar=True)

# Create the formatted annotations using your custom function
formatted_annotations = np.vectorize(custom_annotation)(pivot_table_ir)
# Create a 2D list of formatted strings for the annotations
# formatted_annotations = [[f'rho={val:.2f}' for val in row] for row in pivot_table_ir.values]

print(formatted_annotations)
ax = sns.heatmap(pivot_swarm_quality, annot=formatted_annotations, fmt='', cmap='coolwarm', cbar_kws={'label': r'$\phi_{avg}$',
                                                                                             'ticks':[]},
            annot_kws={'size': 27},
            vmin=0, vmax=1)
ax.figure.axes[-1].yaxis.label.set_size(20)
# plt.title('Best Informed Ratio: Personal Info Weight vs. Communication Noise')

plt_text = r"$\zeta$: "+f"{sn}\nHeterogeneous swarm better: {(1-(one_count / total_cells)) * 100:.2f}%"
plt.title(plt_text,fontsize=28)
# plt.text(5.80, -0.50, plt_text, fontsize=10,
#          verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.5))
plt.text(-0.3, -0.9, "Label in the cells represent the\ninformed ratio with best swarm quality", fontsize=11,
         verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.5))
plt.xlabel(r'$\eta$', fontsize=25)
plt.xticks(fontsize=28)
plt.yticks(fontsize=28)
plt.ylabel(r'$\omega$', fontsize=25)
plt.gca().invert_yaxis()
plt.show()
