from dataclasses import dataclass


@dataclass
class Budget:
    amount: float | str
    budget: float | str
    pk: int = 0
