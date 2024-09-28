from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

def load_heatmap_data(filepath):
    return pd.read_csv(filepath, index_col=0)

def plot_difference_heatmap(df1, df2, x_label,y_label, title):
    difference = df2 - df1
    # sns.heatmap(difference, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.figure(figsize=(10,8))
    ax=sns.heatmap(difference, annot=True, fmt=".2f", cmap='coolwarm', cbar_kws={'label': r'$\phi_{avg}^{0.6}-\phi_{avg}^{1.0}$'},
                annot_kws={'size': 25},vmin=-0.5, vmax=0.5)
    ax.figure.axes[-1].yaxis.label.set_size(20)
    plt.xlabel(x_label,fontsize=25)
    plt.ylabel(y_label,fontsize=25)
    # Increase font size of the tick labels (x and y axis numbers)
    plt.xticks(fontsize=28)  # Increase x-axis numbers
    plt.yticks(fontsize=28)  # Increase y-axis numbers
    plt.title(title,fontsize=25)
    # param_text="w = 1.2\nDifference=\n(ir:0.6 - ir:1.0)"
    param_text="w = 0.6"
    # plt.text(6.8, 0.2, param_text, fontsize=16,
    #          verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
    # plt.savefig(title + '.png')
    plt.gca().invert_yaxis()
    plt.show()
    plt.close()

if __name__ == '__main__':
    filepath = 'fixed_sensor_data/'
    informed_ratio_path1 = 'ir1.0/'
    informed_ratio_path2 = 'ir0.4/'
    fixed_sn_noise_path = 'sn_fixed_0.6/'
    fixed_cn_noise_path = 'cn_fixed_0.6/'
    df_filename_sn_fixed = 'Personal_Info_Weight_vs_Communication_Noise.csv'
    df_filename_cn_fixed = 'Personal_Info_Weight_vs_Sensor_Noise.csv'

    variable_noise_aspect = 'Communication Noise'
    df1_path = filepath + informed_ratio_path1 + fixed_sn_noise_path + df_filename_sn_fixed
    df2_path = filepath + informed_ratio_path2 + fixed_sn_noise_path + df_filename_sn_fixed
    # df1_data = load_heatmap_data(df1_path)
    # df2_data = load_heatmap_data(df2_path)
    # plot_difference_heatmap(df1_data, df2_data, variable_noise_aspect, f'sn_fixed difference {informed_ratio_path2[0:5]} - {informed_ratio_path1[0:5]} sn={fixed_sn_noise_path[9:12]}')
    # variable_noise_aspect = r'Communication Noise ($\eta$)'
    # Y_label = r"Personal Info Weight ($\omega$)"
    variable_noise_aspect = r'Sensor Noise ($\zeta$)'
    Y_label = r'Communication Noise ($\eta$)'
    df1_data = load_heatmap_data("plots_and_heatmaps/fixed_peronal_weight/piw1.0_ir1.0/Sensor_Noise_vs_Communication_Noise.csv")
    df2_data = load_heatmap_data("plots_and_heatmaps/fixed_peronal_weight/piw1.0_ir0.6/Sensor_Noise_vs_Communication_Noise.csv")
    # df1_data = load_heatmap_data("fixed_sensor_data/ir1.0/sn_fixed_0.6/Personal_Info_Weight_vs_Communication_Noise.csv")
    # df2_data = load_heatmap_data("fixed_sensor_data/ir0.6/sn_fixed_0.6/Personal_Info_Weight_vs_Communication_Noise.csv")
    plot_difference_heatmap(df1_data,df2_data,variable_noise_aspect, Y_label,r"$\phi_{avg}^{0.6}-\phi_{avg}^{1.0}$  $\omega=1.0$")