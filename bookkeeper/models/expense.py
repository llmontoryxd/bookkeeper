"""
Описан класс, представляющий расходную операцию
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Expense:
    """
    Расходная операция.
    amount - сумма
    category - id категории расходов
    expense_date - дата расхода
    added_date - дата добавления в бд
    comment - комментарий
    pk - id записи в базе данных
    """
    amount: int | str
    category: int | str
    expense_date: datetime = field(default_factory=datetime.now)
    added_date: datetime = field(default_factory=datetime.now)
    comment: str = ''
    pk: int = 0


@dataclass(slots=True)
class ExpenseWithStringDate:
    """
    Расходная операция, аналогичная Expense, за исключением того,
    что даты в этой операции содержатся в виде строковых переменных.

    Необходима для прохождения mypy тестов.
    """
    amount: int | str
    category: int | str
    expense_date: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    added_date: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    comment: str = ''
    pk: int = 0
