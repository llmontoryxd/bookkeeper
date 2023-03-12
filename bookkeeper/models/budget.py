from dataclasses import dataclass
from typing import Union


@dataclass
class Budget:
    amount: float | str
    budget: float | str
    pk: int = 0
