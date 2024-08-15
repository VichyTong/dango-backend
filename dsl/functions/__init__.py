from abc import ABC, abstractmethod

class DangoFunction(ABC):
    def __init__(self, function_type):
        self.function_type = function_type

    def classify_axis(self, axis):
        if axis in [0, "index"]:
            return 0
        elif axis in [1, "columns"]:
            return 1
        else:
            raise ValueError(f"Invalid axis: {axis}")

    @abstractmethod
    def definition(self):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def to_natural_language(self, *args, **kwargs):
        pass

    def __repr__(self):
        return self.to_natural_language()