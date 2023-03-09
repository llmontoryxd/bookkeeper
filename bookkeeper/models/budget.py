from dataclasses import dataclass


@dataclass
class Budget:
    amount: float
    budget: float
    pk: int = 0
