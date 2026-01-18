from abc import ABC, abstractmethod
import pandas as pd

class BaseGeneral(ABC):
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight 

    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> dict:
        pass
