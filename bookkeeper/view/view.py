"""
Модуль интерфейса
"""

import os
from PySide6 import QtWidgets, QtGui
from bookkeeper.view.expense_tab import ExpenseTab
from bookkeeper.view.category_tab import CategoryTab
from bookkeeper.view.budget_tab import BudgetTab


class View(QtWidgets.QWidget):  # pylint: disable=too-few-public-methods
    """
    Описывает главное окно (собирает все вкладки вместе)

    figures_path - путь к логотипам
    expense_tab - вкладка с расходами
    category_tab - вкладка с категориями
    budget_tab - вкладка бюджета
    """
    def __init__(self) -> None:
        super().__init__()
        self.figures_path = os.path.join(os.getcwd(), 'view', 'figures')
        self.setWindowTitle('Bookkeeper App')
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.figures_path, 'logo.png')))
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        self.tabs.setMovable(True)

        self.expense_tab = ExpenseTab()
        self.category_tab = CategoryTab()
        self.budget_tab = BudgetTab()
        self.tabs.addTab(self.expense_tab, 'Расходы')
        self.tabs.addTab(self.category_tab, 'Категории')
        self.tabs.addTab(self.budget_tab, 'Бюджет')

        layout.addWidget(self.tabs)
