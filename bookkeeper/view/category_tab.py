from PySide6 import QtWidgets, QtGui, QtCore
from bookkeeper.models.category import Category
from typing import Callable, Optional


class CategoryTab(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.cat_table = CategoryTable()
        layout.addWidget(self.cat_table)


class CategoryTable(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.categories = []  # type: list[Category]
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.title = QtWidgets.QLabel('<b>Категории</b>')
        self.cat_table = QtWidgets.QTableWidget()
        self.cat_table.setColumnCount(2)
        self.cat_table.setRowCount(20)
        self.cat_table.setHorizontalHeaderLabels(
            "Категория Родитель".split()
        )
        self.header = self.cat_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.cat_table.setEditTriggers(QtWidgets.QAbstractItemView.
                                       EditTrigger.NoEditTriggers)
        self.cat_table.verticalHeader().hide()

        layout.addWidget(self.title)
        layout.addWidget(self.cat_table)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.add_row = QtGui.QAction('Добавить категорию', self)
        self.delete_row = QtGui.QAction('Удалить категорию', self)
        self.update_row = QtGui.QAction('Изменить категорию', self)
        self.add_row.triggered.connect(self._add_row)  # type: ignore[attr-defined]
        self.delete_row.triggered.connect(self._delete_row)  # type: ignore[attr-defined]
        self.update_row.triggered.connect(self._update_row)  # type: ignore[attr-defined]

        self.addAction(self.add_row)
        self.addAction(self.delete_row)
        self.addAction(self.update_row)

    def set_data(self, categories: list[Category]) -> None:
        self.cat_table.setRowCount(len(categories))
        self.categories = categories
        for i in range(len(categories)):
            self.cat_table.setItem(i, 0, QtWidgets.QTableWidgetItem(categories[i].name))
            if categories[i].parent is None:
                self.cat_table.setItem(i, 1, QtWidgets.QTableWidgetItem(''))
            else:
                for j in range(len(categories)):
                    if str(categories[i].parent) == str(categories[j].pk):
                        self.cat_table.setItem(i, 1,
                                               QtWidgets.QTableWidgetItem(
                                                   categories[j].name))

    def _add_row(self) -> None:
        self.add_menu = AddMenu(self.categories)
        self.add_menu.submitClicked.connect(self._on_add_menu_submit)
        self.add_menu.show()

    def _delete_row(self) -> None:
        self.delete_warning = DeleteWarning()
        self.delete_warning.exec()
        if self.delete_warning.clickedButton() == self.delete_warning.yes_btn:
            assert self.categories is not None
            self.cat_deleter(self.categories[self.cat_table.currentRow()])

    def _update_row(self) -> None:
        assert self.categories is not None
        upd_obj_pk = self.categories[self.cat_table.currentRow()].pk
        self.update_menu = UpdateMenu(upd_obj_pk, self.categories)
        self.update_menu.cat_widget.cat_line.setText(
            self.categories[self.cat_table.currentRow()].name)
        self.placeholder_parent = ''
        for cat in self.categories:
            if self.categories[self.cat_table.currentRow()].parent == cat.pk:
                self.placeholder_parent = cat.name
        for i in range(self.update_menu.par_widget.par_line.count()):
            if self.placeholder_parent == self.update_menu.par_widget.\
                    par_line.itemText(i):
                self.update_menu.par_widget.par_line.setCurrentIndex(i)
        self.update_menu.submitClicked.connect(self._on_update_menu_submit)
        self.update_menu.show()

    def _on_add_menu_submit(self, name: str, parent: Optional[int]) -> None:
        self.cat_adder(name, parent)

    def _on_update_menu_submit(self, pk: int,
                               new_name: str, new_parent: Optional[int]) -> None:
        self.cat_updater(pk, new_name, new_parent)

    def register_cat_adder(self, handler:
                           Callable[[str, Optional[int]], None]) -> None:
        self.cat_adder = handler

    def register_cat_deleter(self, handler:
                             Callable[[Category], None]) -> None:
        self.cat_deleter = handler

    def register_cat_updater(self, handler:
                             Callable[[int, str, Optional[int]], None]) -> None:
        self.cat_updater = handler


class UpdateMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(int, str, object)

    def __init__(self, pk: int, categories: list[Category]) -> None:
        super().__init__()
        self.pk = pk
        self.categories = categories
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Изменение категории')
        self.cat_widget = AddCategory()
        self.par_widget = AddParent(self.categories)
        self.submit_button = QtWidgets.QPushButton('Изменить')
        self.submit_button.clicked.connect(self._submit)  # type: ignore[attr-defined]

        layout.addWidget(self.cat_widget)
        layout.addWidget(self.par_widget)
        layout.addWidget(self.submit_button)

    def _submit(self) -> None:
        self.name = self.cat_widget.cat_line.text()
        par_cur_text = self.par_widget.par_line.currentText()
        if par_cur_text == '':
            self.parent_text = None
        else:
            for i in range(len(self.categories)):
                if par_cur_text == self.categories[i].name:
                    self.parent_text = self.categories[i].pk
        self.submitClicked.emit(self.pk, self.name, self.parent_text)
        self.close()


class AddMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(str, object)

    def __init__(self, categories: list[Category]) -> None:
        super().__init__()
        self.categories = categories
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Добавление категории')
        self.cat_widget = AddCategory()
        self.cat_widget.cat_line.setPlaceholderText('Название категории')
        self.par_widget = AddParent(self.categories)
        self.par_widget.par_line.setCurrentText('')
        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self._submit)  # type: ignore[attr-defined]

        layout.addWidget(self.cat_widget)
        layout.addWidget(self.par_widget)
        layout.addWidget(self.submit_button)

    def _submit(self) -> None:
        self.name = self.cat_widget.cat_line.text()
        if self.name in [c.name for c in self.categories]:
            raise ValueError(f'Категория {self.name} уже существует')
        par_cur_text = self.par_widget.par_line.currentText()
        if par_cur_text == '':
            self.parent_text = None
        else:
            for i in range(len(self.categories)):
                if par_cur_text == self.categories[i].name:
                    self.parent_text = self.categories[i].pk
        self.submitClicked.emit(self.name, self.parent_text)
        self.close()


class AddCategory(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.cat_label = QtWidgets.QLabel('Категория')
        self.cat_line = QtWidgets.QLineEdit()
        layout.addWidget(self.cat_label)
        layout.addWidget(self.cat_line)


class AddParent(QtWidgets.QWidget):
    def __init__(self, categories: list[Category]) -> None:
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.par_label = QtWidgets.QLabel('Родитель')
        self.par_line = QtWidgets.QComboBox()
        for i in range(len(categories)):
            self.par_line.addItem(categories[i].name)
        self.par_line.addItem('')
        layout.addWidget(self.par_label)
        layout.addWidget(self.par_line)


class DeleteWarning(QtWidgets.QMessageBox):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Удаление строки')
        self.setText('Вы действительно'
                     + ' хотите удалить строку? '
                       'Все данные (подкатегории и расходы) будут удалены.')
        self.yes_btn = self.addButton('Да', QtWidgets.QMessageBox.ButtonRole.YesRole)
        self.no_btn = self.addButton('Нет', QtWidgets.QMessageBox.ButtonRole.NoRole)
        self.setIcon(QtWidgets.QMessageBox.Icon.Question)
