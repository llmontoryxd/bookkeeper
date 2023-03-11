from pytestqt.qt_compat import qt_api
import pytest
import threading
from datetime import datetime, timedelta

from bookkeeper.client import Bookkeeper
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.view.view import View
from bookkeeper.view.budget_tab import BudgetTab
from bookkeeper.view.expense_tab import ExpenseTab
from bookkeeper.view.category_tab import CategoryTab, AddMenu, DeleteWarning


@pytest.fixture
def main_client():
    db_path = 'test.db'
    client = Bookkeeper(db_path)
    client.clear_db()
    return client


def test_add_cat(qtbot, main_client):
    name = 'тестовая категория'
    with qtbot.waitExposed(main_client.view):
        main_client.view.show()
    assert main_client.view.isVisible()
    cat_table = main_client.view.category_tab.cat_table
    cat_table.add_row.trigger()
    with qtbot.waitExposed(cat_table.add_menu):
        cat_table.add_menu.show()
    assert cat_table.add_menu.isVisible()
    cat_table.add_menu.cat_widget.cat_line.setText(name)
    cat_table.add_menu.par_widget.par_line.setCurrentText('')
    qtbot.addWidget(cat_table.add_menu.submit_button)
    qtbot.mouseClick(cat_table.add_menu.submit_button, qt_api.QtCore.Qt.MouseButton.LeftButton)

    cats = main_client.cat_repo.get_all({'name': name})
    assert cats[0].name == name
    assert cats[0].parent is None
    assert cat_table.cat_table.item(0, 0).text() == name
    assert cat_table.cat_table.item(0, 1).text() == ''

    child_name = 'тестовый ребенок'
    cat_table.add_row.trigger()
    with qtbot.waitExposed(cat_table.add_menu):
        cat_table.add_menu.show()
    assert cat_table.add_menu.isVisible()
    cat_table.add_menu.cat_widget.cat_line.setText(child_name)
    cat_table.add_menu.par_widget.par_line.setCurrentText(name)
    qtbot.addWidget(cat_table.add_menu.submit_button)
    qtbot.mouseClick(cat_table.add_menu.submit_button, qt_api.QtCore.Qt.MouseButton.LeftButton)

    cats = main_client.cat_repo.get_all()
    assert cats[1].name == child_name
    assert cats[1].parent == cats[0].pk
    assert cat_table.cat_table.item(1, 0).text() == child_name
    assert cat_table.cat_table.item(1, 1).text() == name

    with qtbot.capture_exceptions() as exceptions:
        qtbot.mouseClick(cat_table.add_menu.submit_button, qt_api.QtCore.Qt.MouseButton.LeftButton)
        existent_name = name
        cat_table.add_row.trigger()
        cat_table.add_menu.cat_widget.cat_line.setText(existent_name)
        cat_table.add_menu.par_widget.par_line.setCurrentText('')
        qtbot.addWidget(cat_table.add_menu.submit_button)

    assert len(exceptions) == 1


def test_add_exp(qtbot, main_client):
    cats = [Category(pk=1, name='пирожок', parent=None)]
    main_client.add_cat(cats[0].name, cats[0].parent)
    summ = '12345'
    comment = 'Вкусный'
    date = '2023-02-25 22:22:22'

    exp_table = main_client.view.expense_tab.expense_table
    exp_table.set_categories(main_client.cats)
    exp_table.add_row.trigger()
    with qtbot.waitExposed(exp_table.add_menu):
        exp_table.add_menu.show()
    assert exp_table.add_menu.isVisible()
    exp_table.add_menu.sum_widget.sum_line.setText(summ)
    exp_table.add_menu.cat_widget.cat_box.setCurrentText(exp_table.categories[0].name)
    exp_table.add_menu.com_widget.comment_line.setText(comment)
    exp_table.add_menu.date_widget.date_box.setDateTime(qt_api.QtCore.QDateTime.fromString(
        date, 'yyyy-MM-dd HH:mm:ss'
    ))
    qtbot.addWidget(exp_table.add_menu.submit_button)
    qtbot.mouseClick(exp_table.add_menu.submit_button, qt_api.QtCore.Qt.MouseButton.LeftButton)

    expenses = main_client.exp_repo.get_all()
    assert expenses[0].expense_date == date
    assert expenses[0].amount == summ
    assert expenses[0].comment == comment
    assert expenses[0].category == cats[0].name
    assert exp_table.expenses_table.item(0, 0).text() == date
    assert exp_table.expenses_table.item(0, 1).text() == summ
    assert exp_table.expenses_table.item(0, 2).text() == cats[0].name
    assert exp_table.expenses_table.item(0, 3).text() == comment


def test_update_budget(qtbot, main_client):
    budgets = ['2000', '14000', '60000']
    cats = [Category(pk=1, name='пирожок', parent=None)]
    expenses = [Expense(pk=1, expense_date=datetime.now(), amount=100, category=cats[0].pk,
                        comment=''),
                Expense(pk=2, expense_date=datetime.now()+timedelta(days=1), amount=300,
                        category=cats[0].pk, comment=''),
                Expense(pk=3, expense_date=datetime.now()+timedelta(weeks=2), amount=500,
                        category=cats[0].pk, comment='')]
    main_client.add_cat(cats[0].name, cats[0].parent)
    for expense in expenses:
        main_client.add_exp(expense.expense_date, expense.amount,
                            expense.category, expense.comment)

    budget_table = main_client.view.budget_tab.budget_table
    assert budget_table.budget_table.item(0, 1).text() == '1000'
    assert budget_table.budget_table.item(1, 1).text() == '7000'
    assert budget_table.budget_table.item(2, 1).text() == '30000'
    budget_table.set_expenses(expenses)
    budget_table.update_budget.trigger()
    with qtbot.waitExposed(budget_table.update_menu):
        budget_table.update_menu.show()
    assert budget_table.update_menu.isVisible()
    budget_table.update_menu.day_budget.line.setText(budgets[0])
    budget_table.update_menu.week_budget.line.setText(budgets[1])
    budget_table.update_menu.month_budget.line.setText(budgets[2])
    qtbot.addWidget(budget_table.update_menu.submit_button)


def test_delete_cat(qtbot, main_client, monkeypatch):
    cats = [Category(pk=1, name='отец', parent=None),
            Category(pk=2, name='сын', parent=1),
            Category(pk=3, name='внук', parent=2)]
    main_client.add_cat(cats[0].name, cats[0].parent)
    main_client.add_cat(cats[1].name, cats[1].parent)
    main_client.add_cat(cats[2].name, cats[2].parent)
    exp_date = '2023-02-25 22:22:22'
    exp_summ = '12345'
    exp_comment = 'Вкусный'
    main_client.add_exp(exp_date, exp_summ, cats[0].name, exp_comment)
    main_client.add_exp(exp_date, exp_summ, cats[1].name, exp_comment)
    exp_table = main_client.view.expense_tab.expense_table
    cat_table = main_client.view.category_tab.cat_table
    main_client.view.category_tab.cat_table.set_data(main_client.cats)
    assert cat_table.cat_table.item(1, 0).text() == 'сын'
    assert main_client.cat_repo.get_all()[1].name == 'сын'

    def handle_dialog():
        warning = qt_api.QtWidgets.QApplication.activeWindow()
        if isinstance(warning, DeleteWarning):
            yes_btn = warning.yes_btn
            qtbot.addWidget(yes_btn)
            qtbot.mouseClick(yes_btn, qt_api.QtCore.Qt.MouseButton.LeftButton, delay=1)

    item = cat_table.cat_table.item(1, 0)
    assert item is not None
    cat_table.cat_table.setCurrentItem(item)

    qt_api.QtCore.QTimer.singleShot(100, handle_dialog)
    cat_table.delete_row.trigger()
    cats_in_repo = main_client.cat_repo.get_all()
    expenses = main_client.exp_repo.get_all()
    assert len(cats_in_repo) == 1
    assert cats_in_repo[0].name == cats[0].name
    assert cat_table.cat_table.item(0, 0).text() == cats[0].name
    assert cat_table.cat_table.item(0, 1).text() == ''
    assert len(expenses) == 1
    assert expenses[0].amount == exp_summ
    assert expenses[0].expense_date == exp_date
    assert expenses[0].category == cats[0].name
    assert expenses[0].comment == exp_comment
    assert exp_table.expenses_table.item(0, 0).text() == exp_date
    assert exp_table.expenses_table.item(0, 1).text() == exp_summ
    assert exp_table.expenses_table.item(0, 2).text() == cats[0].name
    assert exp_table.expenses_table.item(0, 3).text() == exp_comment
