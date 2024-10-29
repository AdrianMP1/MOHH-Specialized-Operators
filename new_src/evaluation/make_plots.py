import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


def sort_columns_by_prefix(df):

    columns = df.columns

    first_column = columns[0]
    other_columns = columns[1:]

    sorted_columns = sorted(other_columns, key=lambda col: (col.split('_')[0], col.split('_')[1]))
    sorted_columns = [first_column] + sorted_columns

    sorted_df = df[sorted_columns]

    return sorted_df


def create_repeated_color_code(n):

    # Generate n random colors
    base_colors = np.random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k'], size=n, replace=False)
    base_colors = ["g", "orange", "grey", "r"]
    repeated_colors = [color for color in base_colors for _ in range(2)]

    return repeated_colors


def plot_boxplots_grouped(df, instance_name, folder_path, save = False):
    
    columns = df.columns[1:]
    groups = {}
    for col in columns:
        prefix = col.split('_')[0]

        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(col)

    # Get group size
    group_size = len(next(iter(groups.values())))
    num_pairs = group_size // 2
    color_code = create_repeated_color_code(num_pairs)
    
    # Plot box plots per column, grouped with spaces
    plt.figure(figsize=(10,6))
    positions = []
    tick_labels = []
    current_pos = 1

    colors = []
    for prefix, cols in groups.items():

        # Get the colors
        colors = colors + color_code

        bp = df[cols].boxplot(positions=range(current_pos, current_pos + len(cols)), widths=0.6, patch_artist=True)
        
        #for patch, color in zip(bp.patches, colors):
        #    patch.set_facecolor(color)
        
        positions.extend(range(current_pos, current_pos + len(cols)))
        tick_labels.extend(cols)
        current_pos += len(cols) + 1
    
    for patch, color in zip(bp.patches, colors):
        patch.set_facecolor(color)

    plt.xticks(positions, tick_labels, rotation=90, ha="right")
    plt.title(f"{instance_name} Boxplot")
    plt.ylabel("HV")
    plt.tight_layout()

    if save:
        # Make folder for figures
        figures_folders = os.path.join(folder_path, "Figures")
        os.makedirs(figures_folders, exist_ok=True)

        # Save figure
        save_name = os.path.join(figures_folders, instance_name + ".png")
        plt.savefig(save_name, dpi=400)

    plt.close()
    #plt.show()


def make_figures(folder_path: str):

    #folder_path = "results_evaluation/Lenovo_Legion_2024_10_21_0253_925549"

    instance_files = os.listdir(folder_path)
    instance_files = [instance for instance in instance_files if instance != "initial_solutions"]
    
    for instance in instance_files:
        
        df = pd.read_csv(os.path.join(folder_path, instance))

        # Rename SMS_EMOA to SMSEMOA
        columns: list[str] = df.columns[1:]
        columns = [col.replace("SMS_EMOA", "SMSEMOA") if col.startswith("SMS_EMOA") else col for col in columns]
        columns = [df.columns[0]] + columns
        df.columns = columns

        df = sort_columns_by_prefix(df)

        instance_name = instance.removesuffix(".csv")
        plot_boxplots_grouped(df, instance_name, folder_path, save=True)


if __name__ == "__main__":
    folder_path = "results_evaluation/Lenovo_Legion_2024_10_21_0253_925549"
    make_figures(folder_path)