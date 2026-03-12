from abc import ABC, abstractmethod

class BaseTool(ABC):

    name: str
    description: str
    parameters: dict

    @abstractmethod
    def run(self, **kwargs):
        pass

    def schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }