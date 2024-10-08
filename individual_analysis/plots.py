
import os
import numpy as np
import pandas as pd
#import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from handle_params import Params

from auxiliars.tree_parser import parse_expression
from graphviz_creator import make_graphviz_tree, render_tree

title_fontsize: int = 16
labels_fontsize: int = 14
ticks_fontsize: int = 12

global_slidewindow: int = 3

# Subtrees
ALPHA = 0.01
MAX_SUBTREES = 5
common_subtrees = ["x()", "y()", "sin(x())", "sin(y())", "cos(x())", "cos(y())"]

boxplots_width = 0.5
colors_category = ["limegreen", "darkorange", "crimson"]

colors = (plt.rcParams['axes.prop_cycle'].by_key()['color'])
global_colors = [[int(h[1:][i:i+2],16)/255 for i in (0,2,4)] for h in colors]
        

meanprops = dict(color='green', linestyle='--')
medianprops = dict(color='orange', linestyle='-')
flierprops = dict(markerfacecolor='none', markeredgecolor='k', linewidth=2.5)

plt.rcParams.update({
    "font.size":12,
    "axes.titlesize":16,
    "axes.labelsize":14,
    "xtick.labelsize":12,
    "ytick.labelsize":12,
    "legend.fontsize":14,
    "figure.titlesize":18
})

# Import auxiliar functions
from auxiliars.plots_auxiliars import create_wide_figure, create_subplots_figure
from auxiliars.plots_auxiliars import extract_metric, extract_best_worst
from auxiliars.plots_auxiliars import get_priority, extract_freq_depth
from auxiliars.plots_auxiliars import make_errorband_plot

def hypervolume_plots(data: dict[str,pd.DataFrame], instance_cols: list[str]):

    params = Params()

    plots_path = params["PLOTS_PATH_CURRENT"]

    current_path = os.path.join(plots_path, "fitnessPlots")

    tendency_path = os.path.join(current_path, "tendency")
    boxplots_path = os.path.join(current_path, "boxplots")
    category_path = os.path.join(current_path, "bestMiddleWorst")
    os.makedirs(tendency_path, exist_ok=True)
    os.makedirs(boxplots_path, exist_ok=True)
    os.makedirs(category_path, exist_ok=True)

    num_generations = len(data)
    xticks = (range(0,num_generations), [str(i) for i in range(num_generations)])

    for instance in instance_cols:
        
        # Extract data
        hvs, hvs_metrics = extract_metric(instance, data)

        # Figure title
        title_string = instance.replace("_", " ").removesuffix(" log2(HV)")

        # * Tendency Line
        
        # Make figure
        line_fig, line_ax = create_wide_figure()

        # Figure path
        line_fig_path = os.path.join(tendency_path, instance + ".png")

        line_ax = make_errorband_plot(line_ax, hvs_metrics[:,0], hvs_metrics[:,1], hvs_metrics[:,2])

        line_ax.set_xlabel("Generations")
        line_ax.set_ylabel(r"$log_{2}(HV)$")
        line_ax.set_title(title_string)
        line_ax.grid(axis="y", linestyle="--", alpha=0.8)

        plt.tight_layout()
        line_fig.savefig(line_fig_path, dpi=400)
        plt.close(line_fig)

        # * BoxPlots

        # Make figure
        box_fig, box_ax = create_wide_figure()

        # Figure path
        box_fig_path = os.path.join(boxplots_path, instance + ".png")

        box_ax.boxplot(hvs, positions=xticks[0], widths=boxplots_width,
                       showmeans=True, meanline=True,
                       meanprops=meanprops, medianprops=medianprops,
                       flierprops=flierprops)
        box_ax.set_xticks(xticks[0], xticks[1])
        box_ax.set_xlabel("Generations")
        box_ax.set_ylabel(r"$log_{2}(HV)$")
        box_ax.grid(axis="y", linestyle="--", alpha=0.8)
        box_fig.suptitle(title_string)

        mean_line = Line2D([0],[0], color="green", linestyle="--", label="Mean")
        median_line = Line2D([0],[0], color="orange", linestyle="-", label="Median")
        outlier_marker = Line2D([0],[0], marker='o', linestyle="none", **flierprops, label="Outliers")

        plt.legend(handles=[median_line,mean_line,outlier_marker], loc="center left", bbox_to_anchor=(1,0.5),
                   frameon=False, fontsize=ticks_fontsize)
        plt.tight_layout()
        plt.subplots_adjust(right=0.85)
        box_fig.savefig(box_fig_path, dpi=400)
        plt.close(box_fig)

        # * Best, Middle and Worst
        
        # Make Figure
        category_fig, category_ax = create_wide_figure()

        # Figure path
        category_fig_path = os.path.join(category_path, instance + ".png")

        # Extract data
        best, middle, worst = extract_best_worst(hvs, slide=1)

        x = range(len(best))

        category_ax.plot(x, best  , c=colors_category[0], linestyle="-" , linewidth=1.5, label="Best (Generation)")
        category_ax.plot(x, middle, c=colors_category[1], linestyle="--", linewidth=1.5, label="Middle (Generation)")
        category_ax.plot(x, worst , c=colors_category[2], linestyle="-.", linewidth=1.5, label="Worst (Generation)")

        category_ax.set_xlabel("Generations")
        category_ax.set_ylabel(r"$log_{2}(HV)$")
        category_ax.set_xticks(xticks[0], xticks[1])
        category_ax.grid(axis="y", linestyle="--", alpha=0.8)
        category_fig.suptitle(title_string)

        plt.legend(loc="lower right")
        plt.tight_layout()
        category_fig.savefig(category_fig_path)
        plt.close(category_fig)
        

def structural_plots(data: dict[str,pd.DataFrame], instance_cols: list[str]):

    params = Params()

    plots_path = params["PLOTS_PATH_CURRENT"]

    current_path = os.path.join(plots_path, "structuralPlots")

    os.makedirs(current_path, exist_ok=True)

    num_generations = len(data)
    xticks = (range(0,num_generations), [str(i) for i in range(num_generations)])

    def diversity_plots():
        
        diversity_path = os.path.join(current_path, "diversity")
        os.makedirs(diversity_path, exist_ok=True)

        # Figure paths
        line_fig_path = os.path.join(diversity_path, "diversity_tendency_line.png")
        box_fig_path = os.path.join(diversity_path, "diversity_boxplot.png")

        # * Tendency Lines

        # Make figure
        line_fig, line_ax = create_subplots_figure(2,1,(10,5))
        line_ax: list[Axes] = line_ax.flatten()

        # Make share x axis and enable grid
        for i in range(len(line_ax)):
            line_ax[i].sharex(line_ax[0])
            line_ax[i].grid(axis="y", linestyle="--", alpha=0.8)
            if i == len(line_ax)-1:
                continue
            line_ax[i].tick_params(labelbottom=False)
        
        # Extract metrics
        ted, ted_metrics = extract_metric("TED", data)
        entropy, entropy_metrics = extract_metric("Entropy", data)

        line_ax[0] = make_errorband_plot(line_ax[0], ted_metrics[:,0], ted_metrics[:,1], ted_metrics[:,2])
        line_ax[0].set_ylabel("Edit Distance", fontsize=ticks_fontsize)

        line_ax[1] = make_errorband_plot(line_ax[1], entropy_metrics[:,0], entropy_metrics[:,1], entropy_metrics[:,2], legend=False)
        line_ax[1].set_ylabel("Entropy", fontsize=ticks_fontsize)

        line_ax[0].set_xticks(xticks[0], xticks[1])
        line_fig.text(0.45,0.05,"Generations", va="center", fontsize=labels_fontsize)
        line_fig.text(0.05,0.5,"Diversity Metrics", va="center", rotation="vertical", fontsize=labels_fontsize)
        #line_fig.suptitle("Individuals Diversity")

        # Adjust ylabels
        line_fig.align_ylabels(line_ax)

        # Adjust layout to avoid overlapping
        line_fig.tight_layout(rect=[0.075, 0.075, 1-0.075, 1])

        line_fig.savefig(line_fig_path, dpi=400)
        plt.close(line_fig)

        # * Boxplots
        # Make figure
        box_fig, box_ax = create_wide_figure()

        box_ax.boxplot(ted, positions=xticks[0], widths=0.75,
                    showmeans=True, meanline=True,
                    meanprops=meanprops, medianprops=medianprops,
                    flierprops=flierprops)
        box_ax.set_xticks(xticks[0], xticks[1])
        box_ax.set_xlabel("Generations")
        box_ax.set_ylabel("Tree-Edit Distance")
        #box_fig.suptitle("")
        box_ax.grid(axis="y", linestyle="--", alpha=0.8)

        mean_line = Line2D([0],[0], color="green", linestyle="--", label="Mean")
        median_line = Line2D([0],[0], color="orange", linestyle="-", label="Median")
        outlier_marker = Line2D([0],[0], marker='o', linestyle='none', **flierprops, label="Outliers")

        plt.legend(handles=[median_line,mean_line,outlier_marker], loc="upper right")
        box_fig.savefig(box_fig_path, dpi=400)
        plt.close(box_fig)


    def tree_structure_plots():
        
        structure_path = os.path.join(current_path, "structure")
        category_path = os.path.join(current_path, "bestMiddleWorst")
        os.makedirs(structure_path, exist_ok=True)
        os.makedirs(category_path, exist_ok=True)

        # Figure paths
        line_fig_path = os.path.join(structure_path, "structural_tendency_line.png")
        hist_fig_path = os.path.join(structure_path, "structural_histogram.png")
        category_fig_path = os.path.join(category_path, "bestMiddleWorstStructure.png")

        # * Tendency Lines
        
        # Make figure
        line_fig, line_ax = create_subplots_figure(2,2,(10,8))
        line_ax: list[Axes] = line_ax.flatten()

        # Make share x axis and enable grid
        for i in range(len(line_ax)):
            line_ax[i].sharex(line_ax[0])
            line_ax[i].grid(axis="y", linestyle="--", alpha=0.8)
            line_ax[i].tick_params('x', labelsize=ticks_fontsize) 
            if i >= 2:
                continue
            line_ax[i].tick_params(labelbottom=False)
            
        # Extract metrics
        size, size_metrics = extract_metric("Size", data)
        depth, depth_metrics = extract_metric("MaxDepth", data)
        balance, balance_metrics = extract_metric("Balance", data)
        skewness, skewness_metrics = extract_metric("Skewness", data)

        line_ax[0] = make_errorband_plot(line_ax[0], size_metrics[:,0], size_metrics[:,1], size_metrics[:,2], legend=False)
        line_ax[0].set_ylabel("Num. Nodes", fontsize=ticks_fontsize)

        line_ax[2] = make_errorband_plot(line_ax[2], depth_metrics[:,0], depth_metrics[:,1], depth_metrics[:,2], legend=False)
        line_ax[2].set_xlabel("Generations", fontsize=ticks_fontsize)
        line_ax[2].set_ylabel("Max Depth", fontsize=ticks_fontsize)

        line_ax[1] = make_errorband_plot(line_ax[1], balance_metrics[:,0], balance_metrics[:,1], balance_metrics[:,2])
        line_ax[1].set_ylabel("Tree Balance", fontsize=ticks_fontsize)

        line_ax[3] = make_errorband_plot(line_ax[3], skewness_metrics[:,0], skewness_metrics[:,1], skewness_metrics[:,2], legend=False)
        line_ax[3].set_xlabel("Generations", fontsize=ticks_fontsize)
        line_ax[3].set_ylabel("Tree Skewness", fontsize=ticks_fontsize)

        #line_ax[0].set_xticks(xticks[0], xticks[1])
        #line_fig.text(0.25,0.05,"Generations", va="center", fontsize=labels_fontsize)
        #line_fig.text(0.75,0.05,"Generations", va="center", fontsize=labels_fontsize)

        line_fig.text(0.05,0.5,"Structural Metrics", va="center", rotation="vertical", fontsize=labels_fontsize)
        #line_fig.suptitle("Individuals Diversity")

        # Adjust ylabels
        line_fig.align_ylabels(line_ax)

        # Adjust layout to avoid overlapping
        line_fig.tight_layout(rect=[0.075, 0, 1-0.075, 1])

        line_fig.savefig(line_fig_path, dpi=400)
        plt.close(line_fig)

        # * Best Middle & Worst

        # Make Figure
        category_fig, category_ax = create_subplots_figure(2,2,(10,8))
        category_ax: list[Axes] = category_ax.flatten()

        # Make share x axis and enable grid
        for i in range(len(category_ax)):
            category_ax[i].sharex(category_ax[0])
            category_ax[i].grid(axis="y", linestyle="--", alpha=0.8)
            category_ax[i].tick_params('x', labelsize=ticks_fontsize) 
            if i >= 2:
                continue
            category_ax[i].tick_params(labelbottom=False)

        x_labels = ["", "", "Generations", "Generations"]
        y_labels = ["Num. Nodes", "Tree Balance", "Max Depth", "Tree Skewness"]
        legends = [False, True, False, False]

        for i, metric in enumerate([size, balance, depth, skewness]):

            # Get data
            best, middle, worst = extract_best_worst(metric)

            # Range
            x = range(len(best))

            # Plot lines
            category_ax[i].plot(x, best  , c=colors_category[0], linestyle="-" , linewidth=1.5, label="Best (Generation)")
            category_ax[i].plot(x, middle, c=colors_category[1], linestyle="--", linewidth=1.5, label="Middle (Generation)")
            category_ax[i].plot(x, worst , c=colors_category[2], linestyle="-.", linewidth=1.5, label="Worst (Generation)")

            # Labels
            category_ax[i].set_xlabel(x_labels[i], fontsize=ticks_fontsize)
            category_ax[i].set_ylabel(y_labels[i], fontsize=ticks_fontsize)

            if legends[i]:
                category_ax[i].legend(fontsize=ticks_fontsize)

        # Figure Y label
        category_fig.text(0.05,0.5,"Structural Metrics", va="center", rotation="vertical", fontsize=labels_fontsize)

        # Adjust ylabels
        category_fig.align_ylabels(line_ax)

        # Adjust layout to avoid overlapping
        category_fig.tight_layout(rect=[0.075, 0, 1-0.075, 1])

        category_fig.savefig(category_fig_path, dpi=400)
        plt.close(category_fig)


        # * Histograms

        # Load individuals metrics
        df_path = os.path.join(params["EXPERIMENT_PATH"], "individuals_metrics.csv")
        df = pd.read_csv(df_path, index_col="Name")
        df.drop(columns="Phenotype", axis=1, inplace=True)

        # Make figure
        hist_fig, hist_ax = create_subplots_figure(1,4)
        hist_ax: list[Axes] = hist_ax.flatten()

        bins = 11
        style = {'edgecolor': 'k', 'linewidth': 1.5, 'alpha':0.8}

        hist_ax[0].hist(df["Size"], bins=bins, **style)
        hist_ax[0].set_xlabel("Num. Nodes", fontsize=ticks_fontsize)

        hist_ax[1].hist(df["MaxDepth"], bins=bins, **style)
        hist_ax[1].set_xlabel("Max Depth", fontsize=ticks_fontsize)

        hist_ax[2].hist(df["Balance"], bins=bins, **style)
        hist_ax[2].set_xlabel("Tree Balance", fontsize=ticks_fontsize)

        hist_ax[3].hist(df["Skewness"], bins=bins, **style)
        hist_ax[3].set_xlabel("Tree Skewness", fontsize=ticks_fontsize)

        hist_fig.text(0.05,0.5, "Counts", va="center", rotation="vertical", fontsize=ticks_fontsize)

        hist_fig.tight_layout(rect=[0.075, 0, 1-0.075, 1])
        hist_fig.savefig(hist_fig_path, dpi=400)
        plt.close(hist_fig)

        # * Scatter Plot

        for instance in instance_cols:

            # Make figure name
            fig_name = instance.removesuffix("_log2(HV)")
            label_name = instance.removeprefix("Instance_")
            label_name = label_name.removesuffix("_log2(HV)")

            scatter_fig_path = os.path.join(structure_path, fig_name + "_scatter.png")

            # Make figure
            scatter_fig, scatter_ax = create_subplots_figure(1,4)
            scatter_ax: list[Axes] = scatter_ax.flatten()
            for i in range(len(scatter_ax)):
                scatter_ax[i].sharey(scatter_ax[0])
                if i==0:
                    continue
                scatter_ax[i].tick_params(labelleft=False)

            scatter_ax[0].scatter(df["Size"], df[instance])
            scatter_ax[0].set_xlabel("Num. Nodes", fontsize=ticks_fontsize)

            scatter_ax[1].scatter(df["MaxDepth"], df[instance])
            scatter_ax[1].set_xlabel("Max Depth", fontsize=ticks_fontsize)

            scatter_ax[2].scatter(df["Balance"], df[instance])
            scatter_ax[2].set_xlabel("Tree Balance", fontsize=ticks_fontsize)

            scatter_ax[3].scatter(df["Skewness"], df[instance])
            scatter_ax[3].set_xlabel("Tree Skewness", fontsize=ticks_fontsize)

            scatter_fig.text(0.05,0.5, r"$log_{2}(HV)$", va="center", rotation="vertical", fontsize=ticks_fontsize)
            scatter_fig.suptitle(label_name)

            scatter_fig.tight_layout(rect=[0.075, 0, 1-0.075, 1])
            scatter_fig.savefig(scatter_fig_path, dpi=400)
            plt.close(scatter_fig)

        del df

    diversity_plots()
    tree_structure_plots()


def subtree_plots(kind: str="population"):

    # * Make Paths
    params = Params()
    plots_path = params["PLOTS_PATH_CURRENT"]
    current_path = os.path.join(plots_path, "subtreesPlots")

    population_path = os.path.join(current_path, "population")
    category_path = os.path.join(current_path, "bestMiddleWorst")

    os.makedirs(population_path, exist_ok=True)
    os.makedirs(category_path, exist_ok=True)

    # * Figure parameters
    names = ["Population", "Best", "Middle", "Worst"]
    prefix = ["", "best_", "middle_", "worst_"]
    target_paths = [population_path, category_path, category_path, category_path]

    # * Get Data

    ## * Population
    pop_freq, pop_depths = extract_freq_depth(kind, data_kind="subtrees",
                                               whole_population=True)

    ## * Best Middle & Worst
    best_freq, best_depths = extract_freq_depth(kind, data_kind="subtrees", category="Best")

    middle_freq, middle_depths = extract_freq_depth(kind, data_kind="subtrees", category="Middle")
    
    worst_freq, worst_depths = extract_freq_depth(kind, data_kind="subtrees", category="Worst")

    # Zip data
    iterator = zip((pop_freq, best_freq, middle_freq, worst_freq),
                (pop_depths, best_depths, middle_depths, worst_depths))
    
    for k, (freq, depths) in enumerate(iterator):

        # * Figure Paths
        name = names[k]
        target_path = target_paths[k]
        area_fig_path = os.path.join(target_path, prefix[k] + "stacked_area.png")
        area_filtered_fig_path = os.path.join(target_path, prefix[k] + "stacked_area_filtered.png")
        boxplot_fig_path = os.path.join(target_path, prefix[k] + "depth_distribution.png")

        # * Transform data
        freq_df = pd.DataFrame(freq)

        # Get subtrees
        subtrees = freq_df.columns.tolist()
        subtrees.remove("Generation")

        # Filter the common subtrees to keep more complex structures
        subtrees = list(set(subtrees).difference(set(common_subtrees)))
        freq_df = freq_df[["Generation"] + subtrees]

        freq_df.loc[:,"Total"] = freq_df.loc[:,subtrees].sum(axis=1)
        freq_percent_df = freq_df.loc[:,subtrees].div(freq_df["Total"], axis=0)
        
        # Remove subtrees with low percentage
        alpha = ALPHA
        filtered_colums = [col for col in subtrees if (freq_percent_df[col] >= alpha).any()]

        contribution = freq_percent_df[filtered_colums].sum()

        # Sort the contributions
        sorted_contributions = contribution.sort_values(ascending=False)

        #sorted_df = sorted_contributions.reset_index()
        #sorted_df.columns = ["Subtrees", "Total Contribution"]
        filtered_colums = sorted_contributions.index.tolist()[:MAX_SUBTREES]

        filtered_df = freq_df[["Generation"] + filtered_colums].copy()
        filtered_df["Total"] = filtered_df[filtered_colums].sum(axis=1)
        
        freq_percent_df = filtered_df.loc[:,filtered_colums].div(filtered_df["Total"], axis=0)
        freq_percent_df["Generation"] = filtered_df["Generation"]

        ## * Stacked Area
        area_fig, area_ax = create_wide_figure()

        subtree_labels = [f"Subtree {i+1:02d}" for i in range(len(filtered_colums))]

        area_ax.stackplot(freq_percent_df["Generation"], freq_percent_df[filtered_colums].T,
                          labels=subtree_labels, edgecolor="k", linewidth=2, alpha=0.8)
        
        area_ax.set_xlabel("Generations")
        area_ax.set_ylabel("Percentage")
        area_fig.suptitle(f"Common Subtrees [{name}]")
        plt.legend(loc="center", bbox_to_anchor=(1.15,0.5),
                   frameon=False, fontsize=ticks_fontsize)
        plt.tight_layout()
        plt.subplots_adjust(right=0.8)
        area_fig.savefig(area_fig_path, dpi=400)
        plt.close(area_fig)

        ## * To Syntax Tree
        # Use the phenotype to syntax tree, then to graphviz
        
        new_path = os.path.join(target_path, name.lower())
        os.makedirs(new_path, exist_ok=True)
        for i, subtree in enumerate(filtered_colums):
            
            # Remove empty parentheses
            #! ERROR: Subtree files in individuals directory returns the string of syntax tree,
            #! We need to return the phenotype. For example phenotype = y-x, str(syntax_tree) = -(y(),x())
            #! Fix from metrics.subtree_characteristics & auxiliars.tree
            subtree = subtree.replace("()","")

            # Make syntax tree
            # TODO: Manual fix for subtree, automate it.
            try:
                syntax_tree = parse_expression(subtree)
            except:
                syntax_tree = parse_expression(subtree)
            # Make figure
            graph = make_graphviz_tree(syntax_tree)
            render_tree(graph, file_path=new_path,
                        name=f"subtree{i+1:02d}", expr=subtree)
        
            
        ## * Depth Distribution
        start_gen = 0 if name=="Population" else 1
        generations = [start_gen, len(depths)//2, len(depths) - 1 + start_gen]

        x0 = 0.0    
        distance = 0.5
        x_positions = []
        for _ in range(len(generations)):
            x_positions.append(x0)
            x_new = (x0 + (len(filtered_colums)-1)*distance) + 3*distance
            x0 = x_new

        colors = global_colors[:MAX_SUBTREES]

        box_fig, box_ax = create_wide_figure()
        
        for i, gen in enumerate(generations):
            gen_data = depths[f"Generation_{gen:04d}"]

            variables = []
            for label in filtered_colums:
                try:
                    data = gen_data[label]
                except:
                    data = []
                variables.append(data)
            
            x0 = x_positions[i]
            positions = [x0 + j*distance for j in range(len(filtered_colums))]

            # Get middle tick
            middle = np.median(positions).item()
            x_positions[i] = middle

            boxes = box_ax.boxplot(variables, positions=positions,
                                   widths=(distance/2)*0.8, patch_artist=True,
                                   medianprops=dict(color="k", linestyle="--", linewidth=2.0))
            
            for patch, color in zip(boxes["boxes"], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.8)
        
        box_ax.set_xticks(x_positions, [f"Generation {i}" for i in generations])
        box_ax.set_ylabel("Depth Distribution")

        box_ax.grid(axis="y", linestyle="--", alpha=0.8)
        box_ax.set_xlim(-2*distance, positions[-1]+2*distance)

        legend_handles = [Line2D([0],[0],marker="s",markeredgecolor=colors[j],markerfacecolor=colors[j],markersize=10, linestyle='none',label=label) for j,label in enumerate(subtree_labels)]
        plt.legend(handles=legend_handles, loc="center", bbox_to_anchor=(1.15,0.5),
                   frameon=False, fontsize=ticks_fontsize)
        plt.tight_layout()
        plt.subplots_adjust(right=0.8)
        box_fig.savefig(boxplot_fig_path, dpi=400)
        plt.close(box_fig)
    

def nonterminal_plots(kind: str="population"):

    # * Make paths
    params = Params()
    plots_path = params["PLOTS_PATH_CURRENT"]
    current_path = os.path.join(plots_path, "nonterminalPlots")
    
    population_path = os.path.join(current_path, "population")
    category_path = os.path.join(current_path, "bestMiddleWorst")
    os.makedirs(population_path, exist_ok=True)
    os.makedirs(category_path, exist_ok=True)

    # * Figure parameters
    names = ["Population", "Best", "Middle", "Worst"]
    prefix = ["", "best_", "middle_", "worst_"]
    target_paths = [population_path, category_path, category_path, category_path]

    # * Get Data

    ## * Population
    pop_freq, pop_depths = extract_freq_depth(kind, whole_population=True)

    ## * Best Middle & Worst
    best_freq, best_depths = extract_freq_depth(kind, category="Best")

    middle_freq, middle_depths = extract_freq_depth(kind, category="Middle")
    
    worst_freq, worst_depths = extract_freq_depth(kind, category="Worst")

    # Zip data
    iterator = zip((pop_freq, best_freq, middle_freq, worst_freq),
                (pop_depths, best_depths, middle_depths, worst_depths))
    
    #nonterminals = ["one_point", "convolution", "masked_cross", "sin", "cos",  "+", "-"]
    #nonterminals_norm = [nonterminal+"_percent" for nonterminal in nonterminals]
    #sel_labels = ["one_point", "convolution", "masked_cross"]
    #sel_nonterminals = [label+"_percent" for label in sel_labels]

    for k, (freq, depths) in enumerate(iterator):

        # * Figure Paths
        name = names[k]
        target_path = target_paths[k]
        area_fig_path = os.path.join(target_path, prefix[k] + "stacked_area.png")
        area_filtered_fig_path = os.path.join(target_path, prefix[k] + "stacked_area_filtered.png")
        boxplot_fig_path = os.path.join(target_path, prefix[k] + "depth_distribution.png")

        # * Transform data
        freq_df = pd.DataFrame(freq)
        
        # Get nonterminals
        nonterminals = freq_df.columns.tolist()
        nonterminals.remove("Generation")
        
        nonterminals = sorted(nonterminals, key=get_priority)
        sel_labels = ["one_point", "convolution", "masked_cross"]
        for label in sel_labels:
            if label not in nonterminals:
                sel_labels.remove(label)

        nonterminals_norm = [nonterminal+"_percent" for nonterminal in nonterminals]
        sel_nonterminals = [label+"_percent" for label in sel_labels]

        freq_df["Total"] = freq_df[nonterminals].sum(axis=1)
        for nonterminal in nonterminals:
            freq_df[nonterminal+"_percent"] = freq_df[nonterminal] / freq_df["Total"]
        
        ## * Stacked Area
        area_fig, area_ax = create_wide_figure()

        area_ax.stackplot(freq_df["Generation"], freq_df[nonterminals_norm].T,
                          labels=nonterminals, edgecolor="k", linewidth=2, alpha=0.8)
        area_ax.set_xlabel("Generations")
        area_ax.set_ylabel("Percentage")
        area_fig.suptitle(f"Nonterminals Usage [{name}]")
        plt.legend(loc="center", bbox_to_anchor=(1.15,0.5),
                   frameon=False, fontsize=ticks_fontsize)
        plt.tight_layout()
        plt.subplots_adjust(right=0.8)
        area_fig.savefig(area_fig_path, dpi=400)
        plt.close(area_fig)

        ## * Filtered Stacked Area
        area_fig, area_ax = create_wide_figure()

        area_ax.stackplot(freq_df["Generation"], freq_df[sel_nonterminals].T,
                          labels=sel_labels, edgecolor="k", linewidth=2, alpha=0.8)
        area_ax.set_xlabel("Generations")
        area_ax.set_ylabel("Percentage")
        area_fig.suptitle(f"Nonterminals Usage [{name}]")
        plt.legend(loc="center", bbox_to_anchor=(1.15,0.5),
                   frameon=False, fontsize=ticks_fontsize)
        plt.tight_layout()
        plt.subplots_adjust(right=0.8)
        area_fig.savefig(area_filtered_fig_path, dpi=400)
        plt.close(area_fig)

        ## * Depth Distribution
        start_gen = 0 if name=="Population" else 1
        generations = [start_gen, len(depths)//2, len(depths) - 1 + start_gen]
    
        x_positions = [1.5, 4.5, 7.5]
        colors = global_colors[:3]

        box_fig, box_ax = create_wide_figure()

        for i, gen in enumerate(generations):
            gen_data = depths[f"Generation_{gen:04d}"]

            variables = []
            for label in ["one_point", "convolution", "masked_cross"]:
                try:
                    data = gen_data[label]
                except:
                    data = []
                variables.append(data)

            x0 = x_positions[i]
            positions = [x0-0.5, x0, x0+0.5]

            boxes = box_ax.boxplot(variables, positions=positions,
                            widths=0.3, patch_artist=True,
                            medianprops=dict(color="k", linestyle="--", linewidth=2.0))

            for patch, color in zip(boxes["boxes"], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.8)

        box_ax.set_xticks(x_positions, [f"Generation {i}" for i in generations])
        box_ax.set_ylabel("Depth Distribution")

        box_ax.grid(axis="y", linestyle="--", alpha=0.8)
        box_ax.set_xlim(0.5, 8.5)

        var1_line = Line2D([0],[0], marker='s', markersize=10, markerfacecolor=colors[0], linestyle='none', label="one point")
        var2_line = Line2D([0],[0], marker='s', markersize=10, markerfacecolor=colors[1], linestyle='none', label="convolution")
        var3_line = Line2D([0],[0], marker='s', markersize=10, markerfacecolor=colors[2], linestyle='none', label="masked cross")

        plt.legend(handles=[var1_line,var2_line,var3_line], loc="upper right")
        plt.tight_layout()
        box_fig.savefig(boxplot_fig_path, dpi=400)
        plt.close(box_fig)


def hv_with_tree(data: dict[str, pd.DataFrame]):

    # * Prepare data
    params = Params()
    current_path = params["PLOTS_PATH_CURRENT"]
    individuals_path = params["INDIVIDUALS_PATH"]

    hv_tree_path = os.path.join(current_path, "hv_video", "frames")
    os.makedirs(hv_tree_path, exist_ok=True)

    generations = list(data.keys())[1:]
    num_generations = len(generations)
    
    max_hvs = []
    avg_hvs = []
    avg_ted = []
    best_individuals = []

    for generation in generations:
        current_data: pd.DataFrame = data[generation]

        avg_ted.append(current_data["TED"].mean())
        max_hvs.append(current_data["Instance_KC10-2fl-1rl_log2(HV)"].max()) # TODO: Define the instance, or for all instances??
        avg_hvs.append(current_data["Instance_KC10-2fl-1rl_log2(HV)"].mean())
        best_individuals.append(current_data.index[0])


    # * Prepare plots
    fig = plt.figure(figsize=(10,5))
    ax1 = plt.subplot(2,2,1)
    ax2 = plt.subplot(2,2,3, sharex=ax1)
    ax3 = plt.subplot(1,2,2)
    ax3.axis("off")
    axes = [ax1, ax2, ax3]

    axes[0].set_ylabel(r"$log_{2}(HV)$", fontsize=ticks_fontsize)
    #axes[0].set_title(r"$log_{2}(HV)$", fontsize=labels_fontsize)
    axes[0].tick_params(labelbottom=False)
    axes[1].set_ylabel(f"Tree-Edit Distance", fontsize=ticks_fontsize)
   # axes[1].set_title("Diversity", fontsize=labels_fontsize)
    axes[1].set_xlabel("Generation", fontsize=ticks_fontsize)
    axes[0].set_xlim(1, num_generations)
    axes[0].set_ylim(min(avg_hvs)*0.99, max(max_hvs)*1.01)
    axes[1].set_ylim(min(avg_ted)*0.99, max(avg_ted)*1.01)

    fig.align_ylabels([ax1,ax2])
    plt.tight_layout()

    xdata = []
    ydata = [[], [], []]
    line = [None, None, None]
    line[0], = axes[0].plot(xdata, ydata[0], linewidth=1.5, c=global_colors[1], linestyle="-" , marker="o")
    line[1], = axes[0].plot(xdata, ydata[1], linewidth=1.5, c=global_colors[2], linestyle="--", marker="^")
    line[2], = axes[1].plot(xdata, ydata[2], linewidth=1.5, c='k',              linestyle="-" , marker="o")

    for gen in range(num_generations):
        
        current_hv = max_hvs[gen]
        current_ted = avg_ted[gen]
        current_avg_hv = avg_hvs[gen]
        best_individual = best_individuals[gen]

        # HV line
        xdata.append(gen+1)
        ydata[0].append(current_hv)
        line[0].set_data(xdata, ydata[0])

        # Average HV line
        ydata[1].append(current_avg_hv)
        line[1].set_data(xdata, ydata[1])

        # Diversity line
        ydata[2].append(current_ted)
        line[2].set_data(xdata, ydata[2])
        plt.draw()

        # Draw tree
        individual_path = os.path.join(individuals_path, best_individual, f"Tree_{best_individual}")
        img = plt.imread(individual_path + ".gv.png")
        axes[-1].cla()
        axes[-1].axis("off")
        axes[-1].imshow(img)
        
        # Save frame
        frame_path = os.path.join(hv_tree_path, f"Frame_{gen:03d}.png")
        #plt.pause(0.1)
        fig.savefig(frame_path, dpi=250)
    #plt.show()

from pymoo.indicators.igd_plus import IGDPlus
from pymoo.indicators.hv import HV
from auxiliars.individuals_auxiliars import get_generation_files, load_generation
from auxiliars.file_operations import read_json

def non_dominated_sorting(solutions):
    """
    Compute the non dominated sorting.
    """

    fronts = [[]]
    rank = dict()

    domination_count = dict()
    dominated_solutions = dict()
    
    for p in solutions:
        
        dominated_solutions[p] = []
        domination_count[p] = 0

        # Compute the domination counter of p
        for q in solutions:

            if dominates(p, q):
                # Add q to the set of solutions dominated by p
                dominated_solutions[p].append(q)
            elif dominates(q, p):
                domination_count[p] += 1
        
        # If p belongs to the first front
        if domination_count[p] == 0:
            fronts[0].append(p)
            rank[p] = 0
    return fronts


def dominates(individual1, individual2):
    """
    Return True if individual 1 dominates individual 2, else False.
    """
    sign = -1
    better_in_at_least_one = False

    # Check if A is strictly better than B in at least one objective
    for a, b in zip(individual1, individual2):
        if sign * a < sign * b:
            # If A is worse in any objective, it doesn't dominates B
            return False
        if sign * a > sign * b:
            # If A is better in any objective, mark this condition
            better_in_at_least_one = True
    
    # A dominates B if A is better in at least one objective and
    # equal in the others.

    return better_in_at_least_one

def front_evolution():

    params = Params()

    experiment_path = params["EXPERIMENT_PATH"]
    individuals_path = params["INDIVIDUALS_PATH"]
    generations_path = params["GENERATIONS_PATH"]

    current_path = params["PLOTS_PATH_CURRENT"]
    front_evolution_path = os.path.join(current_path, "frontEvolution")
    os.makedirs(front_evolution_path, exist_ok=True)

    num_generations = len(os.listdir(generations_path))

    instances = get_generation_files(os.path.join(generations_path, "generation_0000"))

    for instance in instances:

        # Adjust instance name for individuals
        individual_instance: str = instance.replace("Instance_Fronts", "instance")

        # Make path
        instance_save_path = os.path.join(front_evolution_path, individual_instance.removesuffix(".json"))
        os.makedirs(instance_save_path, exist_ok=True)

        # To save generation fronts and igd+
        igd_metric = []
        nadir_points = []
        generation_fronts = []
        generation_zerofronts = []

        # Limits
        x_limits = [float("inf"), float("-inf")]
        y_limits = [float("inf"), float("-inf")]

        # * Get data
        for gen in range(num_generations):

            # Get population pointers
            population, offspring = load_generation(gen)

            # Get only the names
            individuals = list(population.keys())

            # Variable to merge fronts
            individual_fronts = list()

            for individual in individuals:
                
                # Make path
                individual_path = os.path.join(individuals_path, individual, individual_instance)

                # Get data
                individual_data = read_json(individual_path)

                # Get Front
                front = individual_data["front"]

                # Get max and min values
                max_values = [max(obj) for obj in zip(*front)]
                min_values = [min(obj) for obj in zip(*front)]

                # Update limits
                if max_values[0] > x_limits[1]:
                    x_limits[1] = max_values[0]

                if min_values[0] < x_limits[0]:
                    x_limits[0] = min_values[0]

                if max_values[1] > y_limits[1]:
                    y_limits[1] = max_values[1]
                
                if min_values[1] < y_limits[0]:
                    y_limits[0] = min_values[1]

                # Add to the generation front
                individual_fronts.append(front)

            # Compute Nadir
            consolidated = set()
            for front in individual_fronts:
                front = set([tuple(point) for point in front])
                consolidated = consolidated.union(front)
            front_zero = non_dominated_sorting(consolidated)[0]
            nadir_point = list(map(max, zip(*front_zero)))
            nadir_points.append(nadir_point)

            # Compute IGD+
            if gen > 0:
                indicator = IGDPlus(np.array(front_zero))
                igd_plus = indicator(generation_zerofronts[gen-1])
                igd_metric.append(igd_plus)
            
            generation_fronts.append(individual_fronts)
            generation_zerofronts.append(np.array(front_zero))

        # * Process data
        last_nadir = nadir_points[-1]
        hv_indicator = HV(ref_point=last_nadir)

        consolidated_fronts = []
        hypervolumes_generations = []

        for gen in range(num_generations):
            
            # Get current data, compute HV with last nadir
            hypervolumes = []
            current_data = generation_fronts[gen]

            for individual_front in current_data:
                hv = hv_indicator(np.array(individual_front))
                
                # If the front is outside nadir's scope, set hv to 0, else log2(hv)
                if hv > 1:
                    log2_hv = np.log2(hv)
                else:
                    log2_hv = 0

                hypervolumes.append(log2_hv)

                if hypervolumes[-1] == float("-inf"):
                    print("Error")
            
            hypervolumes_generations.append(np.mean(hypervolumes).item())

            consolidated = set()
            for front in current_data:
                front = set([tuple(point) for point in front])
                consolidated = consolidated.union(front)
            consolidated = np.array(list(consolidated))
            consolidated_fronts.append(consolidated)

        del generation_fronts, individual_fronts, current_data

        # * Make figure
        fig = plt.figure(figsize=(10,5))

        # Make subplots
        ax1 = plt.subplot(1,2,1)
        ax2 = plt.subplot(2,2,2)
        ax3 = plt.subplot(2,2,4, sharex=ax2)

        ax1.set_title("Population first front")
        ax1.set_xlabel(r"$f_{1}$")
        ax1.set_ylabel(r"$f_{2}$")
        
        ax1.set_xlim(x_limits[0]*0.99, x_limits[1]*1.01)
        ax1.set_ylim(y_limits[0]*0.99, y_limits[1]*1.01)

        ax2.set_title("Hypervolume (Last Nadir-Point)")
        ax2.tick_params(labelbottom=False)
        ax2.set_ylabel(r"$log_{2}(HV)$")
        ax2.set_xlim(0, num_generations)
        ax2.set_ylim(min(hypervolumes_generations)*0.99, max(hypervolumes_generations)*1.01)

        ax3.set_title("Front movement")
        ax3.set_xlabel("Generations")
        ax3.set_ylabel("IGD+")
        ax3.set_ylim(min(igd_metric)*0.99, max(igd_metric)*1.01)
        
        fig.align_ylabels([ax2,ax3])
        plt.tight_layout()


        xdata = []
        ydata = [[],[]]
        line = [None, None]
        line[0], = ax2.plot(xdata, ydata[0], linewidth=1.5, c="r", linestyle="-", marker="o")
        line[1], = ax3.plot(xdata, ydata[1], linewidth=1.5, c=global_colors[9], linestyle="--", marker="^")


        ax1.scatter(last_nadir[0], last_nadir[1], s=70, color="r", marker="*")
        for gen in range(num_generations):
            
            # Plot fronts
            frontzero = generation_zerofronts[gen]
            consolidated = consolidated_fronts[gen]
            
            draw_points = ax1.scatter(consolidated[:,0], consolidated[:,1], s=20, color=global_colors[0])
            frontzero_points = ax1.scatter(frontzero[:,0], frontzero[:,1], s=30, color=global_colors[1])
            current_nadir = ax1.scatter(nadir_points[gen][0], nadir_points[gen][1], s=70, color="tab:green", marker="*")

            # HV line
            xdata.append(gen)
            ydata[0].append(hypervolumes_generations[gen])
            line[0].set_data(xdata, ydata[0])

            # IGD+
            if gen > 0:
                ydata[1].append(igd_metric[gen-1])
                line[1].set_data(xdata[1:], ydata[1])

            plt.draw()

            frame_name = os.path.join(instance_save_path, f"Frame_{gen:03d}.png")
            fig.savefig(frame_name, dpi=250)
            draw_points.remove()
            frontzero_points.remove()
            current_nadir.remove()
            plt.pause(0.01)

        plt.close(fig)




def make_plots(data: dict[str,pd.DataFrame], offspring: bool = False):

    # Note: Data contains a dataframe per generation.

    # Get params
    params = Params()

    # Make subfolders
    if not(offspring):
        kind = "population"
    else:
        kind = "offspring"
    
    params["PLOTS_PATH_CURRENT"] = os.path.join(params["PLOTS_PATH"], kind)

    # Get instances names
    ## Access any dataframe
    df = data[list(data.keys())[0]]
    
    ## Get columns
    columns = df.columns
    instance_columns = sorted(list(set([column for column in columns if column.startswith("Instance")])))

    del df
    
    # First, make HVs plots
    hypervolume_plots(data, instance_columns)

    # Hypervolume with best tree
    hv_with_tree(data)

    # Structural Plots
    structural_plots(data, instance_columns)

    # Subtree plots
    subtree_plots()

    # Function usage
    nonterminal_plots()

    # Correlations & Patterns

    del data
    
    # Pareto fronts
    front_evolution()
    