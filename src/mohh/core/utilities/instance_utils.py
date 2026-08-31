
import os

from mohh.core.params import Params
from mohh.core.utilities.paths import project_root

def instance_paths(train: bool):
    """
    Access the datasets folder and load the files inside.
    """

    params = Params()

    dataset_path = os.path.join(project_root(), "datasets", params["DATASET"])

    if train:
        target_path = os.path.join(dataset_path, "train")
    else:
        target_path = os.path.join(dataset_path, "test")
    
    instances = [os.path.join(target_path, i) for i in os.listdir(target_path)]

    return instances
