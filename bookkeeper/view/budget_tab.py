from PySide6 import QtWidgets, QtGui

budget_data = [[705.43, 1000], [6719.43, 7000], [10592.96, 30000]]


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

        self._set_data()

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.budget_table)

    def _set_data(self):
        for i in range(len(budget_data)):
            self.budget_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(budget_data[i][0])))
            self.budget_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(budget_data[i][1])))
