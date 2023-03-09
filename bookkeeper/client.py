from bookkeeper.view.view import View
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from PySide6 import QtWidgets, QtGui
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget
from bookkeeper.utils import read_tree
import os
import sys


class Bookkeeper:
    def __init__(self):
        self.view = View()
        self.db_path = os.path.join(os.getcwd(), 'databases', 'bookkeeper.db')
        self.cat_repo = SQLiteRepository(self.db_path, Category)
        self.cats = self.cat_repo.get_all()
        self.view.category_tab.cat_table.set_data(self.cats)
        self.view.category_tab.cat_table.register_cat_adder(self.add_cat)
        self.view.category_tab.cat_table.register_cat_deleter(self.delete_cat)
        self.view.category_tab.cat_table.register_cat_updater(self.update_cat)

        self.exp_repo = SQLiteRepository(self.db_path, Expense)
        self.expenses = self.exp_repo.get_all()
        self.view.expense_tab.expense_table.set_categories(self.cats)
        self.view.expense_tab.expense_table.set_data(self.expenses)
        self.view.expense_tab.expense_table.register_expense_adder(self.add_exp)
        self.view.expense_tab.expense_table.register_expense_deleter(self.delete_exp)
        self.view.expense_tab.expense_table.register_expense_updater(self.update_expense)

        self.budget_repo = SQLiteRepository(self.db_path, Budget)
        self.budget_data = self.budget_repo.get_all()
        if len(self.budget_data) == 0:
            self.budget_repo.add(Budget(amount=0, budget=1000))
            self.budget_repo.add(Budget(amount=0, budget=7000))
            self.budget_repo.add(Budget(amount=0, budget=30000))
        self.view.budget_tab.budget_table.set_expenses(self.expenses)
        self.view.budget_tab.budget_table.set_data(self.budget_data)
        self.view.budget_tab.budget_table.register_budget_updater(self.update_budget)

    def add_cat(self, name, parent):
        cat = Category(name, parent)
        self.cat_repo.add(cat)
        self.cats.append(cat)
        self.view.category_tab.cat_table.set_data(self.cats)

    def delete_cat(self, category):
        cat_subs_list = self.find_subs(category, [])
        for cat in cat_subs_list:
            self.cat_repo.delete(cat.pk)
            self.cats.remove(cat)
        self.view.category_tab.cat_table.set_data(self.cats)

    def find_subs(self, category, cat_subs_list):
        cat_subs_list.append(category)
        sub_cats = self.cat_repo.get_all({'parent': category.pk})
        for sub_cat in sub_cats:
            self.find_subs(sub_cat, cat_subs_list)
        return cat_subs_list

    def update_cat(self, pk, new_name, new_parent):
        new_cat = Category(pk=pk, name=new_name, parent=new_parent)
        self.cat_repo.update(new_cat)
        for cat in self.cats:
            if cat.pk == new_cat.pk:
                cat.name = new_cat.name
                cat.parent = new_cat.parent
        self.view.category_tab.cat_table.set_data(self.cats)

    def add_exp(self, date, summ, cat, comment):
        expense = Expense(amount=summ, category=cat, comment=comment, expense_date=date)
        self.exp_repo.add(expense)
        self.expenses.append(expense)
        self.view.expense_tab.expense_table.set_data(self.expenses)
        self.view.budget_tab.budget_table.set_data(self.budget_data)

    def delete_exp(self, expense):
        self.exp_repo.delete(expense.pk)
        self.expenses.remove(expense)
        self.view.expense_tab.expense_table.set_data(self.expenses)
        self.view.budget_tab.budget_table.set_data(self.budget_data)

    def update_expense(self, pk, new_date, new_summ, new_cat, new_com):
        new_expense = Expense(pk=pk, expense_date=new_date, amount=new_summ, category=new_cat, comment=new_com)
        self.exp_repo.update(new_expense)
        for expense in self.expenses:
            if expense.pk == new_expense.pk:
                expense.expense_date = new_expense.expense_date
                expense.amount = new_expense.amount
                expense.category = new_expense.category
                expense.comment = new_expense.comment
        self.view.expense_tab.expense_table.set_data(self.expenses)
        self.view.budget_tab.budget_table.set_data(self.budget_data)

    def update_budget(self, day_budget, week_budget, month_budget, amounts):
        day_budget_data = Budget(pk=1, budget=day_budget, amount=amounts[0])
        week_budget_data = Budget(pk=2, budget=week_budget, amount=amounts[1])
        month_budget_data = Budget(pk=3, budget=month_budget, amount=amounts[2])
        self.budget_repo.update(day_budget_data)
        self.budget_repo.update(week_budget_data)
        self.budget_repo.update(month_budget_data)
        self.budget_data[0].budget = day_budget
        self.budget_data[1].budget = week_budget
        self.budget_data[2].budget = month_budget
        self.view.budget_tab.budget_table.set_data(self.budget_data)


app = QtWidgets.QApplication(sys.argv)
B = Bookkeeper()
B.view.resize(600, 900)
B.view.show()
app.exec()
