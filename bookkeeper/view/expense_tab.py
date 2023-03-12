"""
Модуль, описывающий вкладку расходов
"""

import operator
from datetime import datetime
from typing import Callable
from PySide6 import QtWidgets, QtGui, QtCore
from bookkeeper.models.category import Category
from bookkeeper.models.expense import ExpenseWithStringDate


class ExpenseTab(QtWidgets.QWidget):
    """
    Описывает вкладку расходов

    expense_table - таблица расходов с названием
    """
    def __init__(self) -> None:
        super().__init__()
        self.categories = None
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.expense_table = ExpenseTable()
        layout.addWidget(self.expense_table)


class ExpenseTable(QtWidgets.QWidget):
    """
    Описывает таблицу расходов с названием

    categories - категории из базы данных
    expenses - расходы из базы данных
    update_menu - меню обновления расхода
    add_menu - меню добавления расхода
    delete_warning - предупреждение при удалении расхода
    expense_adder - обертка функции добавления расхода
    expense_deleter - обертка функции удаления расхода
    expense_updater - обертка функции обновления расхода
    title - название таблицы
    expenses_table - таблица расходов
    """
    def __init__(self) -> None:
        super().__init__()
        self.categories = []            # type: list[Category]
        self.expenses = None            # type: list[ExpenseWithStringDate] | None
        self.update_menu = None         # type: UpdateMenu | None
        self.add_menu = None            # type: AddMenu | None
        self.delete_warning = None      # type: DeleteWarning | None
        self.expense_adder: Callable[[str, str, str, str], None] | None = None
        self.expense_deleter: Callable[[ExpenseWithStringDate], None] | None = None
        self.expense_updater: Callable[[int, str, str, str, str], None] | None = None
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
        """
        Получает данные по категориям и записывает их в массив

        Параметры
        ----------
        categories - категории из базы данных

        """
        self.categories = categories

    def set_data(self, expenses: list[ExpenseWithStringDate]) -> None:
        """
        Получает данные по расходам и записывает их в таблицу

        Параметры
        ----------
        expenses - расходы их базы данных

        """
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
        """
        Отображает меню обновления расхода

        """
        assert self.expenses is not None
        upd_obj_pk = self.expenses[self.expenses_table.currentRow()].pk
        self.update_menu = UpdateMenu(upd_obj_pk, self.categories)
        assert self.update_menu is not None
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
        """
        Отображает меню добавления расхода

        """
        self.add_menu = AddMenu(self.categories)
        assert self.add_menu is not None
        self.add_menu.submitClicked.connect(self._on_add_menu_submit)
        self.add_menu.show()

    def _delete_row(self) -> None:
        """
        Отображает предупреждение при удалении расхода

        """
        self.delete_warning = DeleteWarning()
        assert self.delete_warning is not None
        self.delete_warning.exec()
        if self.delete_warning.clickedButton() == self.delete_warning.yes_btn:
            assert self.expenses is not None
            assert self.expense_deleter is not None
            self.expense_deleter(self.expenses[self.expenses_table.currentRow()])

    def _on_add_menu_submit(self, date: str, summ: str, cat: str, comment: str) -> None:
        """
        Обертка функции добавления расхода

        Параметры
        ----------
        date - дата расхода
        summ - сумма расхода
        cat - категория расхода
        comment - комментарий к расходу

        """
        assert self.expense_adder is not None
        self.expense_adder(date, summ, cat, comment)

    def _on_update_menu_submit(self, pk: int, new_date: str,
                               new_summ: str, new_cat: str, new_com: str) -> None:
        """
        Обертка функции обновления расхода

        Параметры
        ----------
        pk - первичный ключ обновляемого расхода
        new_date - новая дата
        new_summ - новая сумма
        new_cat - новая категория
        new_com - новый комментарий

        """
        assert self.expense_updater is not None
        self.expense_updater(pk, new_date, new_summ, new_cat, new_com)

    def register_expense_adder(self,
                               handler: Callable[[str, str, str, str], None]) -> None:
        """
        Инициализирует обертку функции добавления расхода

        Параметры
        ----------
        handler - функция добавления расхода

        """
        self.expense_adder = handler
        assert self.expense_adder is not None

    def register_expense_deleter(self,
                                 handler: Callable[[ExpenseWithStringDate], None]) \
            -> None:
        """
        Инициализирует обертку функции удаления расхода

        Параметры
        ----------
        handler - функция удаления расхода

        """

        self.expense_deleter = handler
        assert self.expense_deleter is not None

    def register_expense_updater(self,
                                 handler: Callable[[int, str, str, str, str], None]) \
            -> None:
        """
        Инициализирует обертку функции обновления расхода

        Параметры
        ----------
        handler - функция обновления расхода

        """
        self.expense_updater = handler
        assert self.expense_updater is not None


class UpdateMenu(QtWidgets.QWidget):
    """
    Описывает меню обновления расхода

    submitClicked - сигнал нажатия кнопки "Изменить"
    pk - номер обновляемого расхода
    categories - категории из базы данных
    sum_widget - виджет записи суммы
    cat_widget - виджет выбора категории
    com_widget - виджет записи комментария
    date_widget - виджет выбора даты
    submit_button - кнопка "Изменить"
    date_from_box - дата из виджета
    date - дата из виджета в строковом виде
    sum - сумма
    cat_text - категория
    com - комментарий
    """
    submitClicked = QtCore.Signal(int, str, str, str, str)

    def __init__(self, pk: int, categories: list[Category]) -> None:
        super().__init__()
        self.pk = pk
        self.categories = categories
        self.date_from_box = None   # type: QtCore.QDateTime | None
        self.date = None            # type: str | None
        self.sum = None             # type: str | None
        self.cat_text = None        # type: str | None
        self.com = None             # type: str | None
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
        """
        Описывает поведение интерфейса при нажатии кнопки "Изменить"

        """
        self.date_from_box = self.date_widget.date_box.dateTime()
        assert self.date_from_box is not None
        self.date = self.date_from_box.toString('yyyy-MM-dd HH:mm:ss')
        self.sum = self.sum_widget.sum_line.text()
        self.cat_text = self.cat_widget.cat_box.currentText()
        self.com = self.com_widget.comment_line.toPlainText()
        assert self.date is not None
        assert self.sum is not None
        assert self.cat_text is not None
        assert self.com is not None
        self.submitClicked.emit(self.pk, self.date, self.sum, self.cat_text, self.com)
        self.close()


class AddMenu(QtWidgets.QWidget):
    """
    Описывает меню добавления расхода

    submitClicked - сигнал нажатия кнопки "Добавить"
    categories - категории из базы данных
    sum_widget - виджет записи суммы
    cat_widget - виджет выбора категории
    com_widget - виджет записи комментария
    date_widget - виджет выбора даты
    submit_button - кнопка "Добавить"
    date_from_box - дата из виджета
    date - дата из виджета в строковом виде
    sum - сумма
    cat_text - категория
    com - комментарий
    """
    submitClicked = QtCore.Signal(str, str, str, str)

    def __init__(self, categories: list[Category]) -> None:
        super().__init__()
        self.categories = categories
        self.date_from_box = None   # type: QtCore.QDateTime | None
        self.date = None            # type: str | None
        self.sum = None             # type: str | None
        self.cat_text = None        # type: str | None
        self.com = None             # type: str | None
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
        """
        Описывает поведение интерфейса при нажатии кнопки "Добавить"

        """
        self.date_from_box = self.date_widget.date_box.dateTime()
        assert self.date_from_box is not None
        self.date = self.date_from_box.toString('yyyy-MM-dd HH:mm:ss')
        self.sum = self.sum_widget.sum_line.text()
        self.cat_text = self.cat_widget.cat_box.currentText()
        self.com = self.com_widget.comment_line.toPlainText()
        assert self.date is not None
        assert self.sum is not None
        assert self.cat_text is not None
        assert self.com is not None
        self.submitClicked.emit(self.date, self.sum, self.cat_text, self.com)
        self.close()


class AddSum(QtWidgets.QWidget):
    """
    Описывает виджет записи суммы с названием

    sum_label - надпись "Сумма"
    sum_line - виджет записи суммы
    """
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.sum_label = QtWidgets.QLabel('Сумма')
        self.sum_line = QtWidgets.QLineEdit()
        layout.addWidget(self.sum_label)
        layout.addWidget(self.sum_line)


class AddCategory(QtWidgets.QWidget):
    """
    Описывает виджет выбора категории с названием

    cat_label - надпись "Категория"
    cat_line - виджет выбора категории
    """
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
    """
    Описывает виджет записи комментария с названием

    comment_label - надпись "Комментарий"
    comment_line - виджет записи комментария
    """
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.comment_label = QtWidgets.QLabel('Комментарий')
        self.comment_line = QtWidgets.QTextEdit()
        layout.addWidget(self.comment_label)
        layout.addWidget(self.comment_line)


class AddDate(QtWidgets.QWidget):
    """
    Описывает виджет выбора даты с названием

    date_label - надпись "Дата"
    date_box - виджет выбора даты
    """
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
    """
    Описывает предупреждение при удалении объекта

    yes_btn - локализированная кнопка подтверждения
    no_btn - локализированная кнопка отклонения
    """
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Удаление расхода')
        self.setText('Вы действительно'
                     + ' хотите удалить строку? Запись о расходе будет удалена.')
        self.yes_btn = self.addButton('Да', QtWidgets.QMessageBox.ButtonRole.YesRole)
        self.no_btn = self.addButton('Нет', QtWidgets.QMessageBox.ButtonRole.NoRole)
        self.setIcon(QtWidgets.QMessageBox.Icon.Question)
