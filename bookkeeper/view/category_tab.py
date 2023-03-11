from PySide6 import QtWidgets, QtGui, QtCore


class CategoryTab(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.cat_table = CategoryTable()
        self.layout.addWidget(self.cat_table)


class CategoryTable(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = None
        self.cat_adder = None
        self.cat_deleter = None
        self.cat_updater = None
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QtWidgets.QLabel('<b>Категории</b>')
        self.cat_table = QtWidgets.QTableWidget()
        self.cat_table.setColumnCount(2)
        self.cat_table.setRowCount(20)
        self.cat_table.setHorizontalHeaderLabels(
            "Категория Родитель".split()
        )
        self.header = self.cat_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)
        self.cat_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.cat_table.verticalHeader().hide()

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.cat_table)

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.add_row = QtGui.QAction('Добавить категорию', self)
        self.delete_row = QtGui.QAction('Удалить категорию', self)
        self.update_row = QtGui.QAction('Изменить категорию', self)
        self.add_row.triggered.connect(self._add_row)
        self.delete_row.triggered.connect(self._delete_row)
        self.update_row.triggered.connect(self._update_row)

        self.addAction(self.add_row)
        self.addAction(self.delete_row)
        self.addAction(self.update_row)

    def set_data(self, categories):
        self.cat_table.setRowCount(len(categories))
        self.categories = categories
        for i in range(len(categories)):
            self.cat_table.setItem(i, 0, QtWidgets.QTableWidgetItem(categories[i].name))
            if categories[i].parent is None:
                self.cat_table.setItem(i, 1, QtWidgets.QTableWidgetItem(''))
            else:
                for j in range(len(categories)):
                    if str(categories[i].parent) == str(categories[j].pk):
                        self.cat_table.setItem(i, 1, QtWidgets.QTableWidgetItem(categories[j].name))

    #def contextMenuEvent(self, event):
    #    print(event.globalPos())
    #    self.context = QtWidgets.QMenu(self)
    #    add_row = QtGui.QAction('Добавить категорию', self)
    #    delete_row = QtGui.QAction('Удалить категорию', self)
    #    update_row = QtGui.QAction('Изменить категорию', self)
    #    self.context.addAction(update_row)
    #    self.context.addAction(add_row)
    #    self.context.addAction(delete_row)
    #    action = self.context.exec(event.globalPos())
    #    if action == add_row:
    #        self._add_row()
    #    elif action == delete_row:
    #        self._delete_row()
    #    elif action == update_row:
    #        self._update_row()

    def _add_row(self):
        self.add_menu = AddMenu(self.categories)
        self.add_menu.submitClicked.connect(self._on_add_menu_submit)
        self.add_menu.show()

    def _delete_row(self):
        self.delete_warning = DeleteWarning()
        self.delete_warning.exec()
        if self.delete_warning.clickedButton() == self.delete_warning.yes_btn:
            self.cat_deleter(self.categories[self.cat_table.currentRow()])

    def _update_row(self):
        upd_obj_pk = self.categories[self.cat_table.currentRow()].pk
        self.update_menu = UpdateMenu(upd_obj_pk, self.categories)
        self.update_menu.cat_widget.cat_line.setText(self.categories[self.cat_table.currentRow()].name)
        placeholder_parent = ''
        for cat in self.categories:
            if self.categories[self.cat_table.currentRow()].parent == cat.pk:
                placeholder_parent = cat.name
        for i in range(self.update_menu.par_widget.par_line.count()):
            if placeholder_parent == self.update_menu.par_widget.par_line.itemText(i):
                self.update_menu.par_widget.par_line.setCurrentIndex(i)
        self.update_menu.submitClicked.connect(self._on_update_menu_submit)
        self.update_menu.show()

    def _on_add_menu_submit(self, name, parent):
        self.cat_adder(name, parent)

    def _on_update_menu_submit(self, pk, new_name, new_parent):
        self.cat_updater(pk, new_name, new_parent)

    def register_cat_adder(self, handler):
        self.cat_adder = handler

    def register_cat_deleter(self, handler):
        self.cat_deleter = handler

    def register_cat_updater(self, handler):
        self.cat_updater = handler


class UpdateMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(int, str, object)

    def __init__(self, pk, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pk = pk
        self.categories = categories
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Изменение категории')
        self.cat_widget = AddCategory()
        self.par_widget = AddParent(self.categories)
        self.submit_button = QtWidgets.QPushButton('Изменить')
        self.submit_button.clicked.connect(self._submit)

        self.layout.addWidget(self.cat_widget)
        self.layout.addWidget(self.par_widget)
        self.layout.addWidget(self.submit_button)

    def _submit(self):
        self.name = self.cat_widget.cat_line.text()
        par_cur_text = self.par_widget.par_line.currentText()
        if par_cur_text == '':
            self.parent = None
        else:
            for i in range(len(self.categories)):
                if par_cur_text == self.categories[i].name:
                    self.parent = self.categories[i].pk
        self.submitClicked.emit(self.pk, self.name, self.parent)
        self.close()


class AddMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(str, object)

    def __init__(self, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = categories
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Добавление категории')
        self.cat_widget = AddCategory()
        self.cat_widget.cat_line.setPlaceholderText('Название категории')
        self.par_widget = AddParent(self.categories)
        self.par_widget.par_line.setCurrentText('')
        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self._submit)

        self.layout.addWidget(self.cat_widget)
        self.layout.addWidget(self.par_widget)
        self.layout.addWidget(self.submit_button)

    def _submit(self):
        self.name = self.cat_widget.cat_line.text()
        if self.name in [c.name for c in self.categories]:
            raise ValueError(f'Категория {self.name} уже существует')
        par_cur_text = self.par_widget.par_line.currentText()
        if par_cur_text == '':
            self.parent = None
        else:
            for i in range(len(self.categories)):
                if par_cur_text == self.categories[i].name:
                    self.parent = self.categories[i].pk
        self.submitClicked.emit(self.name, self.parent)
        self.close()


class AddCategory(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.cat_label = QtWidgets.QLabel('Категория')
        self.cat_line = QtWidgets.QLineEdit()
        self.layout.addWidget(self.cat_label)
        self.layout.addWidget(self.cat_line)


class AddParent(QtWidgets.QWidget):
    def __init__(self, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.par_label = QtWidgets.QLabel('Родитель')
        self.par_line = QtWidgets.QComboBox()
        for i in range(len(categories)):
            self.par_line.addItem(categories[i].name)
        self.par_line.addItem('')
        self.layout.addWidget(self.par_label)
        self.layout.addWidget(self.par_line)


class DeleteWarning(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Удаление строки')
        self.setText('Вы действительно'
            +' хотите удалить строку? Все данные (подкатегории и расходы) будут удалены.')
        self.yes_btn = self.addButton('Да', QtWidgets.QMessageBox.ButtonRole.YesRole)
        self.no_btn = self.addButton('Нет', QtWidgets.QMessageBox.ButtonRole.NoRole)
        self.setIcon(QtWidgets.QMessageBox.Icon.Question)
