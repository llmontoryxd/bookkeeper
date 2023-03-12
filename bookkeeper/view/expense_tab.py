from PySide6 import QtWidgets, QtGui, QtCore
from datetime import datetime
from typing import Callable
from bookkeeper.models.category import Category
from bookkeeper.models.expense import ExpenseWithStringDate
import operator


class ExpenseTab(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.categories = None
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.expense_table = ExpenseTable()
        layout.addWidget(self.expense_table)


class ExpenseTable(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.categories = []            # type: list[Category]
        self.expenses = None            # type: list[ExpenseWithStringDate] | None
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.title = QtWidgets.QLabel('<b>Последние расходы</b>')
        self.expenses_table = QtWidgets.QTableWidget()
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split()
        )
        self.header = self.expenses_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.v_header = self.expenses_table.verticalHeader()
        self.v_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.
                                           ResizeToContents)
        self.expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.
                                            EditTrigger.NoEditTriggers)
        self.expenses_table.verticalHeader().hide()

        layout.addWidget(self.title)
        layout.addWidget(self.expenses_table)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.add_row = QtGui.QAction('Добавить расход', self)
        self.delete_row = QtGui.QAction('Удалить расход', self)
        self.update_row = QtGui.QAction('Изменить расход', self)
        self.add_row.triggered.connect(self._add_row)  # type: ignore[attr-defined]
        self.delete_row.triggered.connect(self._delete_row)  # type: ignore[attr-defined]
        self.update_row.triggered.connect(self._update_row)  # type: ignore[attr-defined]

        self.addAction(self.add_row)
        self.addAction(self.delete_row)
        self.addAction(self.update_row)

    def set_categories(self, categories: list[Category]) -> None:
        self.categories = categories

    def set_data(self, expenses: list[ExpenseWithStringDate]) -> None:
        self.expenses = sorted(expenses, key=operator.attrgetter('expense_date'),
                               reverse=True)
        self.expenses_table.setRowCount(len(self.expenses))
        for i in range(len(self.expenses)):
            date = self.expenses[i].expense_date
            self.expenses_table.setItem(i, 0,
                                        QtWidgets.QTableWidgetItem(date))
            self.expenses_table.setItem(i, 1,
                                        QtWidgets.QTableWidgetItem(
                                            self.expenses[i].amount))
            self.expenses_table.setItem(i, 2,
                                        QtWidgets.QTableWidgetItem(
                                            self.expenses[i].category))
            self.expenses_table.setItem(i, 3,
                                        QtWidgets.QTableWidgetItem(
                                            self.expenses[i].comment))

    def _update_row(self) -> None:
        assert self.expenses is not None
        upd_obj_pk = self.expenses[self.expenses_table.currentRow()].pk
        self.update_menu = UpdateMenu(upd_obj_pk, self.categories)
        self.update_menu.sum_widget.sum_line.setText(str(self.expenses[
                                                         self.expenses_table.
                                                         currentRow()].amount))
        self.update_menu.com_widget.comment_line.setText(self.expenses[
                                                         self.expenses_table.
                                                         currentRow()].comment)
        date = QtCore.QDateTime.fromString(self.expenses[
                                           self.expenses_table.currentRow()].expense_date,
                                           'yyyy-MM-dd HH:mm:ss')
        self.update_menu.date_widget.date_box.setDateTime(date)
        placeholder_cat = self.expenses[self.expenses_table.currentRow()].category
        for i in range(self.update_menu.cat_widget.cat_box.count()):
            if self.update_menu.cat_widget.cat_box.itemText(i) == placeholder_cat:
                self.update_menu.cat_widget.cat_box.setCurrentIndex(i)
        self.update_menu.submitClicked.connect(self._on_update_menu_submit)
        self.update_menu.show()

    def _add_row(self) -> None:
        self.add_menu = AddMenu(self.categories)
        self.add_menu.submitClicked.connect(self._on_add_menu_submit)
        self.add_menu.show()

    def _delete_row(self) -> None:
        self.delete_warning = DeleteWarning()
        self.delete_warning.exec()
        if self.delete_warning.clickedButton() == self.delete_warning.yes_btn:
            assert self.expenses is not None
            self.expense_deleter(self.expenses[self.expenses_table.currentRow()])

    def _on_add_menu_submit(self, date: str, summ: str, cat: str, comment: str) -> None:
        self.expense_adder(date, summ, cat, comment)

    def _on_update_menu_submit(self, pk: int, new_date: str,
                               new_summ: str, new_cat: str, new_com: str) -> None:
        self.expense_updater(pk, new_date, new_summ, new_cat, new_com)

    def register_expense_adder(self, handler:
                               Callable[[str, str, str, str], None]) -> None:
        self.expense_adder = handler

    def register_expense_deleter(self, handler:
                                 Callable[[ExpenseWithStringDate], None]) -> None:
        self.expense_deleter = handler

    def register_expense_updater(self, handler:
                                 Callable[[int, str, str, str, str], None]) -> None:
        self.expense_updater = handler


class UpdateMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(int, str, str, str, str)

    def __init__(self, pk: int, categories: list[Category]) -> None:
        super().__init__()
        self.pk = pk
        self.categories = categories
        layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle('Изменение расхода')
        self.setLayout(layout)
        self.sum_widget = AddSum()
        self.cat_widget = AddCategory(self.categories)
        self.com_widget = AddComment()
        self.date_widget = AddDate()
        self.submit_button = QtWidgets.QPushButton('Изменить')
        self.submit_button.clicked.connect(self._submit)  # type: ignore[attr-defined]

        layout.addWidget(self.date_widget)
        layout.addWidget(self.sum_widget)
        layout.addWidget(self.cat_widget)
        layout.addWidget(self.com_widget)
        layout.addWidget(self.submit_button)

    def _submit(self) -> None:
        self.date_from_box = self.date_widget.date_box.dateTime()
        self.date = self.date_from_box.toString('yyyy-MM-dd HH:mm:ss')
        self.sum = self.sum_widget.sum_line.text()
        self.cat_text = self.cat_widget.cat_box.currentText()
        self.com = self.com_widget.comment_line.toPlainText()
        self.submitClicked.emit(self.pk, self.date, self.sum, self.cat_text, self.com)
        self.close()


class AddMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(str, str, str, str)

    def __init__(self, categories: list[Category]) -> None:
        super().__init__()
        self.categories = categories
        layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle('Добавление расхода')
        self.setLayout(layout)
        self.sum_widget = AddSum()
        self.sum_widget.sum_line.setPlaceholderText('0')
        self.cat_widget = AddCategory(self.categories)
        self.com_widget = AddComment()
        self.com_widget.comment_line.setPlaceholderText('Введите комментарий...')
        self.date_widget = AddDate()
        self.date_widget.date_box.setDateTime(QtCore.QDateTime.fromString(
                                              datetime.now().strftime(
                                                  '%Y-%m-%d %H:%M:%S'),
                                              'yyyy-MM-dd HH:mm:ss'))
        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self._submit)  # type: ignore[attr-defined]

        layout.addWidget(self.date_widget)
        layout.addWidget(self.sum_widget)
        layout.addWidget(self.cat_widget)
        layout.addWidget(self.com_widget)
        layout.addWidget(self.submit_button)

    def _submit(self) -> None:
        self.date_from_box = self.date_widget.date_box.dateTime()
        self.date = self.date_from_box.toString('yyyy-MM-dd HH:mm:ss')
        self.sum = self.sum_widget.sum_line.text()
        self.cat_text = self.cat_widget.cat_box.currentText()
        self.com = self.com_widget.comment_line.toPlainText()
        self.submitClicked.emit(self.date, self.sum, self.cat_text, self.com)
        self.close()


class AddSum(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.sum_label = QtWidgets.QLabel('Сумма')
        self.sum_line = QtWidgets.QLineEdit()
        layout.addWidget(self.sum_label)
        layout.addWidget(self.sum_line)


class AddCategory(QtWidgets.QWidget):
    def __init__(self, categories: list[Category]) -> None:
        super().__init__()
        self.categories = categories
        assert self.categories is not None
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.cat_label = QtWidgets.QLabel('Категория')
        self.cat_box = QtWidgets.QComboBox()
        for i in range(len(self.categories)):
            self.cat_box.addItem(self.categories[i].name)
        layout.addWidget(self.cat_label)
        layout.addWidget(self.cat_box)


class AddComment(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.comment_label = QtWidgets.QLabel('Комментарий')
        self.comment_line = QtWidgets.QTextEdit()
        layout.addWidget(self.comment_label)
        layout.addWidget(self.comment_line)


class AddDate(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.date_label = QtWidgets.QLabel('Дата')
        self.date_box = QtWidgets.QDateTimeEdit()
        self.date_box.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_box)


class DeleteWarning(QtWidgets.QMessageBox):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Удаление расхода')
        self.setText('Вы действительно'
                     + ' хотите удалить строку? Запись о расходе будет удалена.')
        self.yes_btn = self.addButton('Да', QtWidgets.QMessageBox.ButtonRole.YesRole)
        self.no_btn = self.addButton('Нет', QtWidgets.QMessageBox.ButtonRole.NoRole)
        self.setIcon(QtWidgets.QMessageBox.Icon.Question)
