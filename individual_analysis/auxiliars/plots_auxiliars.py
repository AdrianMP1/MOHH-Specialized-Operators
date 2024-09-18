
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from handle_params import Params
from auxiliars.file_operations import read_json

from plots import global_slidewindow

def create_wide_figure() -> tuple[Figure, Axes]:

    fig, ax = plt.subplots(1,1,figsize=(10,5))
    return fig, ax


def create_subplots_figure(nrows: int, ncols: int, sizes:tuple=(10,5)) -> tuple[Figure, list[Axes]]:

    fig, ax = plt.subplots(nrows, ncols, figsize=sizes)
    return fig, ax


def extract_metric(name: str, data: dict[str,pd.DataFrame]) -> tuple[list[list], np.ndarray]:

    raw_data = []
    summarized = []

    num_gen = len(data)

    for gen in range(num_gen):

        df = data[f"Generation_{gen:03d}"].copy()

        var_data = df[name].tolist()

        raw_data.append(var_data)

        min_val = min(var_data)
        max_val = max(var_data)
        med_val = np.median(var_data).item()
        summarized.append([min_val, max_val, med_val])
    
    summarized = np.array(summarized)

    return raw_data, summarized


def extract_best_worst(metric: list[list], slide: int=global_slidewindow):
    """
    """
    best_data = []
    middle_data = []
    worst_data = []
    for gen in range(1,len(metric)):
        
        gen_data = metric[gen]
        middle_point = len(gen_data) // 2

        best = np.mean(gen_data[:slide]).item()
        middle = np.mean(gen_data[middle_point - slide//2 - 1 : middle_point+slide//2]).item()
        worst = np.mean(gen_data[-slide:]).item()

        best_data.append(best)
        middle_data.append(middle)
        worst_data.append(worst)
    
    return best_data, middle_data, worst_data


def make_errorband_plot(ax: Axes, min_vals: list,
                    max_vals: list, med_vals: list, legend: bool=True) -> Axes:
    
    generations = list(range(len(min_vals)))

    # Interpolate max and min values
    #new_x = np.linspace(generations[0], generations[-1], num=100)
    #new_min_vals = np.interp(new_x, generations, min_vals)
    #new_max_vals = np.interp(new_x, generations, max_vals)

    # Make four plot lines
    #ax.plot(new_x, new_min_vals)
    #ax.plot(new_x, new_max_vals)
    ax.plot(generations, min_vals, label="Min")
    ax.plot(generations, max_vals, label="Max")

    #ax.plot(generations, avg_vals, linestyle="--")
    ax.plot(generations, med_vals, linestyle="-.", label="Median")

    # Make shaded area
    ax.fill_between(generations, min_vals, max_vals, alpha=0.2)

    if legend:
        ax.legend()

    return ax


def merge_individuals_keys(freq: list[dict], depths: list[dict], 
                                   keys_history: list[str]):
    gen_freq = {}
    gen_depths = {}

    for individual in freq:
        for hash_key, count in individual.items():
            generation_count = gen_freq.get(hash_key, 0)
            gen_freq[hash_key] = generation_count + count

            # Add to known keys
            if hash_key not in keys_history:
                keys_history.append(hash_key)
            
    for individual in depths:
        for hash_key, depths in individual.items():
            generation_count: list = gen_depths.get(hash_key, [])
            generation_count.extend(depths)
            gen_depths[hash_key] = generation_count
            
    return gen_freq, gen_depths


def merge_generation_keys(gen_freq: dict[str,int], gen_depths: dict[str,list],
                hist_freq: dict[str,list], hist_depths: dict[str,dict],
                keys_history: list, gen: int):
            
    for hash_key in keys_history:

        # Frequencies
        generation_count = gen_freq.get(hash_key, 0)

        # Get the historical count
        history_count: list = hist_freq.get(hash_key, [])

        if not(history_count):
            # Fill with zeros previous generations
            history_count = [0]*(len(hist_freq["Generation"]) - 1)
                
        # Append frequency of this generation
        history_count.append(generation_count)
        hist_freq[hash_key] = history_count

        # Depths
        generation_depths = gen_depths.get(hash_key, [])

        # Note: We can't fill previous generations in case the key is new.            
        hist_depths[f"Generation_{gen:04d}"][hash_key] = generation_depths

    return hist_freq, hist_depths


def extract_freq_depth(kind: str, data_kind: str="non_terminals",
                        whole_population: bool=False,
                        category: str="Best") -> tuple[dict, dict]:

    # * Note: For subtrees, only use whole_population = False

    params = Params()
    generations_path = params["GENERATIONS_PATH"]
    individuals_path = params["INDIVIDUALS_PATH"]

    start_gen = 0 if whole_population else 1
    num_generations = len(os.listdir(generations_path))

    slide = global_slidewindow
    category = category.lower()

    if not(whole_population):    
        if category == "best":
            left, right = None, slide
        elif category == "worst":
            left, right = -slide, None
    else:
        left, right = None, None

    # Allocate variables
    hist_freq: dict[str,list] = {}
    hist_depths: dict[str, dict] = {}
    keys_history = []

    for gen in range(start_gen, num_generations):

        # Get paths
        current_gen_path = os.path.join(generations_path, f"generation_{gen:04d}")
        individuals_pointers_path = os.path.join(current_gen_path, kind + ".json")

        # Get individuals pointers list
        individuals = read_json(individuals_pointers_path)

        if not(whole_population) and category == "middle":
            middle_point = len(individuals) // 2
            left = middle_point - slide//2 - 1
            right = middle_point + slide//2
        
        # Filter the individuals to analyze
        individuals = individuals[left:right]

        # Add generation data
        hist_freq["Generation"] = hist_freq.get("Generation", []) + [gen]
        hist_depths[f"Generation_{gen:04d}"] = {}

        # Allocate individuals data
        individuals_freq: list[dict] = []
        individuals_depths: list[dict] = []

        for individual in individuals:
            current_individual_path = os.path.join(individuals_path, individual)

            kind_freq_path = os.path.join(current_individual_path, data_kind + "_frequency.json")
            kind_depth_path = os.path.join(current_individual_path, data_kind + "_depths.json")

            frequencies: dict = read_json(kind_freq_path)
            depths: dict = read_json(kind_depth_path)

            individuals_freq.append(frequencies)
            individuals_depths.append(depths)
        
        # Merge individuals data
        gen_freq, gen_depths = merge_individuals_keys(individuals_freq, individuals_depths, keys_history)

        # Merge with historical data
        hist_freq, hist_depths = merge_generation_keys(gen_freq, gen_depths, hist_freq,
                                                        hist_depths, keys_history, gen)
    
    # Fix hist_depths
    # At this point freq_data has all new keys with filled zeros in old generations.
    # depth_data doesn't have filled values
    for gen in hist_depths.keys():
        current_data = hist_depths[gen]

        generation_keys = list(current_data.keys())

        for hash_key in keys_history:
            if hash_key not in generation_keys:
                current_data[hash_key] = []

    return hist_freq, hist_depths


def get_priority(item):
    primary_keys = ["one_point", "convolution", "masked_cross"]
    secondary_keys = ["sin", "cos"]
    third_keys = ["+", "-"]

    if item in primary_keys:
        return (0, primary_keys.index(item))
    elif item in secondary_keys:
        return (1, secondary_keys.index(item))
    elif item in third_keys:
        return (2, third_keys.index(item))
    else:
        return (3, item)

