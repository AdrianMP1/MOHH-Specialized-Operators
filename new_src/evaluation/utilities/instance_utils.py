
import os

from evaluation.params import Params

def instance_paths(train: bool=False):
    """
    Access the datasets folder and load the files inside.
    """

    params = Params()

    dataset_path = os.path.join(os.getcwd(), "datasets", params["DATASET"])

    if train:
        target_path = os.path.join(dataset_path, "train")
    else:
        target_path = os.path.join(dataset_path, "test")
    
    instances = [os.path.join(target_path, i) for i in os.listdir(target_path)]

    return instances
