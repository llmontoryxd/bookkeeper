"""
Модель бюджета
"""
from dataclasses import dataclass


@dataclass
class Budget:
    """
    Описывает бюджет.

    amount - сумма расходов за определенный период
    budget - заданный бюджет на определенный период
    pk - первчиный ключ записи бюджета на определенный период
    """
    amount: float | str
    budget: float | str
    pk: int = 0
