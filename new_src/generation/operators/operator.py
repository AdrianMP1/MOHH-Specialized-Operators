
from abc import ABC, abstractmethod

class GeneticOperator(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def run(self):
        """
        Execute the operator
        
        :return: Offsprings
        """
