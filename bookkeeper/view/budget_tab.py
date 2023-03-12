from PySide6 import QtWidgets, QtGui, QtCore
from datetime import datetime
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import ExpenseWithStringDate
from typing import Callable, Tuple


class BudgetTab(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.budget_table = BudgetTable()
        layout.addWidget(self.budget_table)


class BudgetTable(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.expenses = []  # type: list[ExpenseWithStringDate]
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.title = QtWidgets.QLabel('<b>Бюджет</b>')
        self.budget_table = QtWidgets.QTableWidget()
        self.budget_table.setColumnCount(2)
        self.budget_table.setRowCount(3)
        self.budget_table.setHorizontalHeaderLabels(
            "Сумма Бюджет".split()
        )
        self.budget_table.setVerticalHeaderLabels(
            "День Неделя Месяц".split()
        )
        self.header = self.budget_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.budget_table.setEditTriggers(QtWidgets.QAbstractItemView.
                                          EditTrigger.NoEditTriggers)

        layout.addWidget(self.title)
        layout.addWidget(self.budget_table)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.update_budget = QtGui.QAction('Обновить бюджет', self)
        self.update_budget.triggered.connect(  # type: ignore[attr-defined]
            self._update_budget)

        self.addAction(self.update_budget)

    def set_expenses(self, expenses: list[ExpenseWithStringDate]) -> None:
        self.expenses = expenses

    def set_data(self, budget_data: list[Budget]) -> None:
        self.now = datetime.now()
        day_amount = 0.0
        week_amount = 0.0
        month_amount = 0.0
        for expense in self.expenses:
            expense_datetime = datetime.fromisoformat(expense.expense_date)
            if expense_datetime.year == self.now.year:
                if expense_datetime.month == self.now.month:
                    month_amount += float(expense.amount)
                    if expense_datetime.isocalendar().week == self.now.isocalendar().week:
                        week_amount += float(expense.amount)
                        if expense_datetime.day == self.now.day:
                            day_amount += float(expense.amount)

        self.budget_table.setItem(0, 0, QtWidgets.QTableWidgetItem(
            str(round(day_amount, 2))))
        self.budget_table.setItem(1, 0, QtWidgets.QTableWidgetItem(
            str(round(week_amount, 2))))
        self.budget_table.setItem(2, 0, QtWidgets.QTableWidgetItem(
            str(round(month_amount, 2))))

        for i in range(len(budget_data)):
            self.budget_table.setItem(i, 1,
                                      QtWidgets.QTableWidgetItem(
                                          str(budget_data[i].budget)))

    def get_data_from_table(self) -> Tuple[Budget, Budget, Budget]:
        day_budget_data = Budget(pk=1, budget=self.budget_table.item(0, 1).text(),
                                 amount=self.budget_table.item(0, 0).text())
        week_budget_data = Budget(pk=1, budget=self.budget_table.item(1, 1).text(),
                                  amount=self.budget_table.item(1, 0).text())
        month_budget_data = Budget(pk=1, budget=self.budget_table.item(2, 1).text(),
                                   amount=self.budget_table.item(2, 0).text())

        return day_budget_data, week_budget_data, month_budget_data

    def _update_budget(self) -> None:
        amounts = [self.budget_table.item(0, 0).text(),
                   self.budget_table.item(1, 0).text(),
                   self.budget_table.item(2, 0).text()]
        self.update_menu = UpdateMenu(amounts)
        self.update_menu.day_budget.line.setText(self.budget_table.item(0, 1).text())
        self.update_menu.week_budget.line.setText(self.budget_table.item(1, 1).text())
        self.update_menu.month_budget.line.setText(self.budget_table.item(2, 1).text())
        self.update_menu.submitClicked.connect(self._on_update_menu_submit)
        self.update_menu.show()

    def _on_update_menu_submit(self, day_budget: str, week_budget: str,
                               month_budget: str, amounts: list[str]) -> None:
        self.budget_updater(day_budget, week_budget, month_budget, amounts)

    def register_budget_updater(self, handler:
                                Callable[[str, str, str, list[str]], None]) -> None:
        self.budget_updater = handler


class UpdateMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(str, str, str, object)

    def __init__(self, amounts: list[str]) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.amounts = amounts
        self.setLayout(layout)
        self.setWindowTitle('Обновление бюджета')
        self.day_budget = AddBudget('День')
        self.week_budget = AddBudget('Неделя')
        self.month_budget = AddBudget('Месяц')
        self.submit_button = QtWidgets.QPushButton('Обновить')
        self.submit_button.clicked.connect(self._submit)  # type: ignore[attr-defined]

        layout.addWidget(self.day_budget)
        layout.addWidget(self.week_budget)
        layout.addWidget(self.month_budget)
        layout.addWidget(self.submit_button)

    def _submit(self) -> None:
        self.day_text = self.day_budget.line.text()
        self.week_text = self.week_budget.line.text()
        self.month_text = self.month_budget.line.text()
        self.submitClicked.emit(self.day_text, self.week_text,
                                self.month_text, self.amounts)
        self.close()


class AddBudget(QtWidgets.QWidget):
    def __init__(self, period: str) -> None:
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.label = QtWidgets.QLabel(period)
        self.line = QtWidgets.QLineEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.line)
