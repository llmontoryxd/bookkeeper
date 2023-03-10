from PySide6 import QtWidgets, QtGui, QtCore
from datetime import datetime


class BudgetTab(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.budget_table = BudgetTable()
        self.layout.addWidget(self.budget_table)


class BudgetTable(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.budget_updater = None
        self.expenses = None
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

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
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)
        self.budget_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.budget_table)

    def set_expenses(self, expenses):
        self.expenses = expenses

    def set_data(self, budget_data):
        now = datetime.now()
        day_amount = 0.0
        week_amount = 0.0
        month_amount = 0.0
        for expense in self.expenses:
            expense_datetime = datetime.fromisoformat(expense.expense_date)
            if expense_datetime.year == now.year:
                if expense_datetime.month == now.month:
                    month_amount += float(expense.amount)
                    if expense_datetime.isocalendar().week == now.isocalendar().week:
                        week_amount += float(expense.amount)
                        if expense_datetime.day == now.day:
                            day_amount += float(expense.amount)

        self.budget_table.setItem(0, 0, QtWidgets.QTableWidgetItem(str(day_amount)))
        self.budget_table.setItem(1, 0, QtWidgets.QTableWidgetItem(str(week_amount)))
        self.budget_table.setItem(2, 0, QtWidgets.QTableWidgetItem(str(month_amount)))

        for i in range(len(budget_data)):
            self.budget_table.setItem(i, 1,
                                      QtWidgets.QTableWidgetItem(str(budget_data[i].budget)))

    def contextMenuEvent(self, event):
        context = QtWidgets.QMenu(self)
        update_budget = QtGui.QAction('Обновить бюджет', self)
        context.addAction(update_budget)

        action = context.exec(event.globalPos())
        if action == update_budget:
            self._update_budget()

    def _update_budget(self):
        amounts = [self.budget_table.item(0, 0).text(),
                   self.budget_table.item(1, 0).text(),
                   self.budget_table.item(2, 0).text()]
        self.update_menu = UpdateMenu(amounts)
        self.update_menu.submitClicked.connect(self._on_update_menu_submit)
        self.update_menu.show()

    def _on_update_menu_submit(self, day_budget, week_budget, month_budget, amounts):
        self.budget_updater(day_budget, week_budget, month_budget, amounts)

    def register_budget_updater(self, handler):
        self.budget_updater = handler


class UpdateMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(str, str, str, object)

    def __init__(self, amounts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.amounts = amounts
        self.setLayout(self.layout)
        self.setWindowTitle('Обновление бюджета')
        self.day_budget = AddBudget('День')
        self.week_budget = AddBudget('Неделя')
        self.month_budget = AddBudget('Месяц')
        self.submit_button = QtWidgets.QPushButton('Обновить')
        self.submit_button.clicked.connect(self._submit)

        self.layout.addWidget(self.day_budget)
        self.layout.addWidget(self.week_budget)
        self.layout.addWidget(self.month_budget)
        self.layout.addWidget(self.submit_button)

    def _submit(self):
        self.day_text = self.day_budget.line.text()
        self.week_text = self.week_budget.line.text()
        self.month_text = self.month_budget.line.text()
        self.submitClicked.emit(self.day_text, self.week_text, self.month_text, self.amounts)
        self.close()


class AddBudget(QtWidgets.QWidget):
    def __init__(self, period, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QtWidgets.QLabel(period)
        self.line = QtWidgets.QLineEdit()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line)
