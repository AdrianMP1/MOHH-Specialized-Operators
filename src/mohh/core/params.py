
class Params:
    _instance = None # Store singleton instance
    _params = {}     # Store the parameters

    def __new__(cls):
        # Check if an instance already exists
        if not cls._instance:
            # Create a new instance
            cls._instance = super(Params, cls).__new__(cls)

        # Return singleton instance
        return cls._instance

    # Overload operators to make the class
    # similar to a python dictionary

    # Get attributes
    def __getitem__(self, key):
        return self._params.get(key)

    # Set attributes
    def __setitem__(self, key, value):
        self._params[key] = value

    # Access params
    def get_params(self):
        return self._params

    # Update the whole params dictionary
    def update_params(self, new_params):
        self._params.update(new_params)

    # Get keys
    def keys(self):
        return self._params.keys()

    # Get values
    def values(self):
        return self._params.values()

    # Get items
    def items(self):
        return self._params.items()

    # Reset instance
    @classmethod
    def reset_instance(cls):
        cls._instance = None
