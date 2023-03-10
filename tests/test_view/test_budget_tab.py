from pytestqt.qt_compat import qt_api
from bookkeeper.view.budget_tab import BudgetTab, AddBudget, UpdateMenu


def test_budget_tab_create(qtbot):
    budget_tab = BudgetTab()
    qtbot.addWidget(budget_tab)


def test_add_budget_create(qtbot):
    add_budget = AddBudget('День')
    qtbot.addWidget(add_budget)


def test_add_update_menu_create(qtbot):
    amounts = ['0', '1', '10']
    update_menu = UpdateMenu(amounts)
    qtbot.addWidget(update_menu)