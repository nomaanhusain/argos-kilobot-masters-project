from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd


def load_heatmap_data(filepath):
    return pd.read_csv(filepath, index_col=0)


def plot_heatmap(heatmap, title, x_label, y_label):
    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(heatmap, annot=True, cmap='coolwarm', cbar_kws={'label': r'$\phi_{avg}$'}, annot_kws={'size': 25},
                vmin=0.2, vmax=0.8)
    ax.figure.axes[-1].yaxis.label.set_size(20)
    plt.xlabel(x_label, fontsize=25)
    plt.xticks(fontsize=28)
    plt.ylabel(y_label, fontsize=25)
    plt.yticks(fontsize=28)
    plt.title(title, fontsize=25)
    plt.gca().invert_yaxis()
    plt.show()


root_directory = "fixed_sensor_data/"
file_name= "Personal_Info_Weight_vs_Communication_Noise.csv"
plot_title=r"$\rho=0.6$ $\zeta=0.4$"
df = load_heatmap_data(root_directory + "ir0.6/sn_fixed_0.4/" + file_name)
df = df.sort_index().sort_index(axis=1)
plot_heatmap(df, plot_title,r'Communication Noise ($\eta$)', r'Personal Info Weight ($\omega$)')
