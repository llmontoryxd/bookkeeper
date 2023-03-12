"""
Основной модуль, обеспечивающий взаимодействие интерфейса и базы данных
"""
from typing import Optional
from bookkeeper.view.view import View
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.expense import Expense, ExpenseWithStringDate
from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget


class Bookkeeper:
    """
    Описывает взаимодействие интерфейса и базы данных.
    view - интерфейс
    db_path - путь к базе данных
    cat_repo - репозиторий категорий
    cats - категории
    exp_repo - репозиторий расходов
    expenses - расходы
    budget_repo - репозиторий бюджета
    budget_data - данные о бюджете и сумме расходов за определенный период
    """
    def __init__(self, db_path: str) -> None:
        self.view = View()
        self.view.resize(600, 900)
        self.db_path = db_path
        self.cat_repo: SQLiteRepository[Category] = SQLiteRepository(self.db_path,
                                                                     Category)
        self.cats = self.cat_repo.get_all()
        self.view.category_tab.cat_table.set_data(self.cats)
        self.view.category_tab.cat_table.register_cat_adder(self.add_cat)
        self.view.category_tab.cat_table.register_cat_deleter(self.delete_cat)
        self.view.category_tab.cat_table.register_cat_updater(self.update_cat)

        self.exp_repo: SQLiteRepository[ExpenseWithStringDate] = \
            SQLiteRepository(self.db_path, Expense)
        self.expenses = self.exp_repo.get_all()
        self.view.expense_tab.expense_table.set_categories(self.cats)
        self.view.expense_tab.expense_table.set_data(self.expenses)
        self.view.expense_tab.expense_table.register_expense_adder(self.add_exp)
        self.view.expense_tab.expense_table.register_expense_deleter(self.delete_exp)
        self.view.expense_tab.expense_table.register_expense_updater(self.update_expense)

        self.budget_repo: SQLiteRepository[Budget] = SQLiteRepository(self.db_path,
                                                                      Budget)
        self.budget_data = self.budget_repo.get_all()
        if len(self.budget_data) == 0:
            self.budget_repo.add(Budget(amount=0, budget=1000))
            self.budget_repo.add(Budget(amount=0, budget=7000))
            self.budget_repo.add(Budget(amount=0, budget=30000))
        self.view.budget_tab.budget_table.set_expenses(self.expenses)
        self.view.budget_tab.budget_table.set_data(self.budget_data)
        self.view.budget_tab.budget_table.register_budget_updater(self.update_budget)

    def add_cat(self, name: str, parent: int | None) -> None:
        """
        Добавляет категорию с/без родителем/я в баззу данных
        и обновляет отображение интерфейса

        Параметры
        ----------
        name - имя категории для добавления
        parent - id родителя категории

        """
        cat = Category(name, parent)
        self.cat_repo.add(cat)
        self.cats.append(cat)
        self.view.category_tab.cat_table.set_data(self.cats)

    def delete_cat(self, category: Category) -> None:
        """
        Удаляет категорию, все подкатегории и расходы, связанные
        с этими категориями, из база данных и обновляет
        отображение интерфейса

        Параметры
        ----------
        category - объект категории для удаления

        """
        cat_subs_list = self.find_subs(category, [])
        for cat in cat_subs_list:
            self.cat_repo.delete(cat.pk)
            self.cats.remove(cat)
            for expense in self.expenses:
                if expense.category == cat.name:
                    self.exp_repo.delete(expense.pk)
                    self.expenses.remove(expense)

        self.view.category_tab.cat_table.set_data(self.cats)
        self.view.expense_tab.expense_table.set_data(self.expenses)
        self.view.budget_tab.budget_table.set_expenses(self.expenses)
        self.view.budget_tab.budget_table.set_data(self.budget_data)
        budgets = self.view.budget_tab.budget_table.get_data_from_table()
        amounts = [str(budgets[0].amount), str(budgets[1].amount), str(budgets[2].amount)]
        self.update_budget(str(budgets[0].budget), str(budgets[1].budget),
                           str(budgets[2].budget), amounts)

    def find_subs(self, category: Category,
                  cat_subs_list: list[Category]) -> list[Category]:
        """
        Функция поиска подкатегорий

        Параметры
        ----------
        category - категория
        cat_subs_list - массив, в который будут записываться подкатегории
        (вместе с изначальной)

        """
        cat_subs_list.append(category)
        sub_cats = self.cat_repo.get_all({'parent': category.pk})
        for sub_cat in sub_cats:
            self.find_subs(sub_cat, cat_subs_list)
        return cat_subs_list

    def update_cat(self, pk: int, new_name: str, new_parent: Optional[int]) -> None:
        """
        Обновляет категорию с pk = pk в базе данных и обновляет отображение интерфейса

        Параметры
        ----------
        pk - первичный ключ категории в базе данных
        new_name - новое имя категории
        new_parent - новый родитель категории

        """
        new_cat = Category(pk=pk, name=new_name, parent=new_parent)
        old_cat = self.cat_repo.get_all({'pk': pk})[0]
        self.cat_repo.update(new_cat)
        for cat in self.cats:
            if cat.pk == new_cat.pk:
                cat.name = new_cat.name
                cat.parent = new_cat.parent

        for expense in self.expenses:
            if expense.category == old_cat.name:
                new_expense = ExpenseWithStringDate(pk=expense.pk,
                                                    expense_date=expense.expense_date,
                                                    amount=expense.amount,
                                                    category=new_name,
                                                    comment=expense.comment)
                self.exp_repo.update(new_expense)
                expense.category = new_name

        self.view.category_tab.cat_table.set_data(self.cats)
        self.view.expense_tab.expense_table.set_data(self.expenses)

    def add_exp(self, date: str, summ: str, cat: str, comment: str) -> None:
        """
        Добавляет расход определенной категории в базу данных и обновляет
        отображение интерфейса

        Параметры
        ----------
        date - дата расхода
        summ - сумма расхода
        cat - категория
        comment - комментарий

        """
        expense = ExpenseWithStringDate(amount=summ, category=cat,
                                        comment=comment, expense_date=date)
        self.exp_repo.add(expense)
        self.expenses = self.exp_repo.get_all()
        self.view.expense_tab.expense_table.set_data(self.expenses)
        self.view.budget_tab.budget_table.set_expenses(self.expenses)
        self.view.budget_tab.budget_table.set_data(self.budget_data)
        budgets = self.view.budget_tab.budget_table.get_data_from_table()
        amounts = [str(budgets[0].amount), str(budgets[1].amount), str(budgets[2].amount)]
        self.update_budget(str(budgets[0].budget), str(budgets[1].budget),
                           str(budgets[2].budget), amounts)

    def delete_exp(self, expense: ExpenseWithStringDate) -> None:
        """
        Удаляет расход из базы данных и обновляет отображение интерфейса

        Параметры
        ----------
        expense - объект расхода

        """
        self.exp_repo.delete(expense.pk)
        self.expenses.remove(expense)
        self.view.expense_tab.expense_table.set_data(self.expenses)
        self.view.budget_tab.budget_table.set_expenses(self.expenses)
        self.view.budget_tab.budget_table.set_data(self.budget_data)
        budgets = self.view.budget_tab.budget_table.get_data_from_table()
        amounts = [str(budgets[0].amount), str(budgets[1].amount), str(budgets[2].amount)]
        self.update_budget(str(budgets[0].budget), str(budgets[1].budget),
                           str(budgets[2].budget), amounts)

    def update_expense(self, pk: int, new_date: str,
                       new_summ: str, new_cat: str, new_com: str) -> None:
        """
        Обновление расхода с pk = pk в базе данных и обновление отображения интерфейса

        Параметры
        ----------
        pk - первичный ключ обновляемого расхода
        new_date - новая дата
        new_summ = новая сумма
        new_cat - новая категория
        new_com - новый комментарий

        """
        new_expense = ExpenseWithStringDate(pk=pk, expense_date=new_date,
                                            amount=new_summ, category=new_cat,
                                            comment=new_com)
        self.exp_repo.update(new_expense)
        self.expenses = self.exp_repo.get_all()
        for expense in self.expenses:
            if expense.pk == new_expense.pk:
                expense.expense_date = new_date
                expense.amount = new_expense.amount
                expense.category = new_expense.category
                expense.comment = new_expense.comment
        self.view.expense_tab.expense_table.set_data(self.expenses)
        self.view.budget_tab.budget_table.set_expenses(self.expenses)
        self.view.budget_tab.budget_table.set_data(self.budget_data)
        budgets = self.view.budget_tab.budget_table.get_data_from_table()
        amounts = [str(budgets[0].amount), str(budgets[1].amount), str(budgets[2].amount)]
        self.update_budget(str(budgets[0].budget), str(budgets[1].budget),
                           str(budgets[2].budget), amounts)

    def update_budget(self, day_budget: str, week_budget: str,
                      month_budget: str, amounts: list[str]) -> None:
        """
        Обновление данных по бюджету в базе данных и обновление отображения
        интерфейса

        Параметры
        ----------
        day_budget - дневной бюджет
        week_budget - недельный бюджет
        month_budget - месячный бюджет
        amounts - сумма по расходам на каждый период


        """
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

    def clear_db(self) -> None:
        """
        Очистка базы данных

        """
        for expense in self.expenses:
            self.exp_repo.delete(expense.pk)
        self.expenses = []
        for cat in self.cats:
            self.cat_repo.delete(cat.pk)
        self.cats = []
        for budget in self.budget_data:
            self.budget_repo.delete(budget.pk)
        self.budget_repo.add(Budget(amount=0, budget=1000))
        self.budget_repo.add(Budget(amount=0, budget=7000))
        self.budget_repo.add(Budget(amount=0, budget=30000))
        self.view.budget_tab.budget_table.set_data(self.budget_data)
