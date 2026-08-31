
import inspect
import importlib

def find_module(module_name: str, operator_name: str, **kwargs: dict) -> object:
    """
    Find a module and initialize it.
    """
    
    try:
        # Import module.
        module = importlib.import_module(module_name)
        
    except ModuleNotFoundError:
        s = f"Error: Specified module not found: {module_name}"
        raise Exception(s)
        
    if not kwargs:
        kwargs = dict()

    # Find the class in the module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if name == operator_name:
            return obj(**kwargs)
    else:
        msg = f"Operator '{operator_name}' not found."
        raise ValueError(msg)
        