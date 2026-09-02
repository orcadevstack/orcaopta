from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class CloudNode:
    id: str
    name: str
    status: str


class CloudBackend(ABC):
    @abstractmethod
    def list_nodes(self) -> List[CloudNode]:
        ...

    @abstractmethod
    def list_storage(self):
        ...

    @abstractmethod
    def list_network(self):
        ...

    @abstractmethod
    def heal(self, issue):
        ...

    @abstractmethod
    def backend_name(self) -> str:
        ...
