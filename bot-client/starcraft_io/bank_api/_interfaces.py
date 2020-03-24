from abc import ABC
from typing import *

class Dumpable(ABC):
    def dump(self) -> Iterator[str]:
        raise NotImplementedError

__all__ = \
[
    'Dumpable',
]
