from abc import ABC, abstractmethod


class GptFunction(ABC):
    def __init__(self, name):
        self.name = name
        self.descriptor = self.get_descriptor()

    @abstractmethod
    def get_descriptor(self) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def run(self) -> str:
        raise NotImplementedError()
