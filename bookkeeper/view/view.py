import sys
import os

from PySide6 import QtWidgets, QtGui
from bookkeeper.view.expense_tab import ExpenseTab
from bookkeeper.view.category_tab import CategoryTab
from bookkeeper.view.budget_tab import BudgetTab

figures_path = os.path.join(os.getcwd(), 'figures')


class View(QtWidgets.QWidget): # pylint: disable=too-few-public-methods
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Bookkeeper App')
        self.setWindowIcon(QtGui.QIcon(os.path.join(figures_path, 'logo.png')))
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabs.setMovable(True)

        self.expense_tab = ExpenseTab()
        self.category_tab = CategoryTab()
        self.budget_tab = BudgetTab()
        self.tabs.addTab(self.expense_tab, 'Расходы')
        self.tabs.addTab(self.category_tab, 'Категории')
        self.tabs.addTab(self.budget_tab, 'Бюджет')

        self.layout.addWidget(self.tabs)

