import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

solver_names = ["MOEAD", "NSGAII", "SMSEMOA"]

def sort_columns_by_prefix(df):

    columns = df.columns

    first_column = columns[0]
    other_columns = columns[1:]

    # Custom order
    custom_order = ["SBX", "PMX", "Best", "Middle", "Worst"]

    # Map for custom order
    type_order_index = {key: i for i, key in enumerate(custom_order)}

    # Sort by Solver, then by type, then by mutation
    sorted_columns = sorted(other_columns, key=lambda x: (
        x.split("_")[0], # Solver
        type_order_index.get(x.split("_")[1], float("inf")), # Type
        x.split("_")[2] # Mutation
    ))

    sorted_columns = [first_column] + sorted_columns

    sorted_df = df[sorted_columns]

    return sorted_df


def create_repeated_color_code(n):

    # Generate n random colors
    base_colors = np.random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k'], size=n, replace=False)
    base_colors = ["grey", "cadetblue", "limegreen", "orange", "red"]
    #repeated_colors = [color for color in base_colors for _ in range(2)]
    repeated_colors = base_colors * n

    return repeated_colors


def plot_boxplots_grouped(df, instance_name, folder_path,
                         solver_used, boundaries,
                         with_mutation=False, save=False):
    
    columns = df.columns[1:]
    groups = {}
    for col in columns:
        prefix = col.split('_')[0]

        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(col)

    # Get group size
    #group_size = len(next(iter(groups.values())))
    #num_pairs = group_size // 2
    
    num_groups = len(groups)
    color_code = create_repeated_color_code(num_groups)
    
    # Plot box plots per column, grouped with spaces
    plt.figure(figsize=(10,6))
    positions = []
    tick_labels = []
    current_pos = 1

    colors = []
    for prefix, cols in groups.items():

        # Get the colors
        #colors = colors + color_code

        bp = df[cols].boxplot(positions=range(current_pos, current_pos + len(cols)), widths=0.6, patch_artist=True,
                              medianprops=dict(color="k", linewidth=2))
        
        #for patch, color in zip(bp.patches, colors):
        #    patch.set_facecolor(color)
        
        positions.extend(range(current_pos, current_pos + len(cols)))
        current_pos += len(cols) + 1

        cols = [" ".join(col.split("_")[:-1]) for col in cols]
        tick_labels.extend(cols)
    
    for patch, color in zip(bp.patches, color_code):
        patch.set_facecolor(color)

    plt.xticks(positions, tick_labels, rotation=90, ha="right")

    mutation_label = "WM" if with_mutation else "NM"
    plt.title(f"{instance_name} - {mutation_label} - ({solver_used}) Box plots")
    
    plt.ylim(boundaries)
    plt.ylabel("HV")

    plt.tight_layout()

    if save:
        # Make folder for figures
        figures_folders = os.path.join(folder_path, "Figures")
        mutation_folder = os.path.join(figures_folders, "WithMutation")
        no_mutation_folder = os.path.join(figures_folders, "NoMutation")
        
        # Save figures
        if with_mutation:
            os.makedirs(mutation_folder, exist_ok=True)
            save_name = os.path.join(mutation_folder, instance_name + "_WM" + ".png")
        
        else:
            os.makedirs(no_mutation_folder, exist_ok=True)
            save_name = os.path.join(no_mutation_folder, instance_name + "_NM" + ".png")

        plt.savefig(save_name, dpi=400)

    plt.close()
    #plt.show()


def make_figures(folder_path: str):

    # Compute the limits of all solutions per instance (Visual purposes)
    instance_boundaries = {}

    for solver in solver_names:

        solver_path = os.path.join(folder_path, solver)

        instance_files = os.listdir(solver_path)

        for instance in instance_files:

            if instance == "Figures":
                continue

            # Load dataframe
            df = pd.read_csv(os.path.join(solver_path, instance))

            instance_name = instance.removesuffix(".csv")

            # Get max and min values
            max_hv = df.iloc[:,1:].max().max()
            min_hv = df.iloc[:,1:].min().min()

            # Load actual boundaries
            new_boundaries = instance_boundaries.get(instance_name, [float("inf"), float("-inf")])
            
            # Extract values
            current_min_hv = new_boundaries[0]
            current_max_hv = new_boundaries[1]

            # Compare
            if current_min_hv > min_hv:
                new_boundaries[0] = min_hv
            
            if current_max_hv < max_hv:
                new_boundaries[1] = max_hv

            # Update boundaries
            instance_boundaries[instance_name] = new_boundaries

    # Increase each extrema by 5%
    for key, (low, high) in instance_boundaries.items():
        interval_range = high - low
        new_low = low - 0.05 * interval_range
        new_high = high + 0.05 * interval_range
        instance_boundaries[key] = [new_low, new_high]

    # Make plots
    for solver in solver_names:

        solver_path = os.path.join(folder_path, solver)

        instance_files = os.listdir(solver_path)
        
        for instance in instance_files:

            if instance == "Figures":
                continue

            df = pd.read_csv(os.path.join(solver_path, instance))

            df = sort_columns_by_prefix(df)

            instance_name = instance.removesuffix(".csv")
            
            # Divide by Mutation and No-Mutation
            whole_columns = df.columns
            no_mutation_cols = ["Experiment"] + [col for col in whole_columns if "_NM_" in col]
            mutation_cols    = ["Experiment"] + [col for col in whole_columns if "_WM_" in col]

            # Plot without mutation
            plot_boxplots_grouped(df[no_mutation_cols], instance_name, solver_path, solver, instance_boundaries[instance_name], save=True)

            # Plot with mutation
            plot_boxplots_grouped(df[mutation_cols], instance_name, solver_path, solver, instance_boundaries[instance_name], with_mutation=True, save=True)


if __name__ == "__main__":
    folder_path = "results_evaluation/"
    make_figures(folder_path)