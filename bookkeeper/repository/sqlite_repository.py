"""
Модуль, описывающий репозиторий, работающий с базой данных
"""

import sqlite3
from inspect import get_annotations
from typing import Any
from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Описывает взаимодействие с базой данных

    db_file - путь к базе данных
    table_name - название таблицы
    fields - поля
    cls - класс таблицы
    """
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls
        self.create_table()

    def _row_to_obj(self, row: tuple[Any] | None) -> Any:
        """
        Преобразовывает строку в объект

        Параметры
        ----------
        row - строка

        """
        if row is None:
            return None
        obj = self.cls(**dict(zip({'pk': int} | self.fields, row)))

        return obj

    def create_table(self) -> None:
        """
        Создает таблицу в базе данных

        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name}('
                        + 'pk INTEGER PRIMARY KEY, '
                        + ', '.join(self.fields.keys()) + ')')
        con.close()

    def drop_table(self) -> None:
        """
        Уничтожает таблицу в базе данных

        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'DROP TABLE IF EXISTS {self.table_name}')
        con.close()

    def add(self, obj: T) -> int:
        """
        Добавляет объект в базу данных

        Параметры
        ----------
        obj - объект для добавления


        """
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled ''pk'' attribute')
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'INSERT INTO {self.table_name} ({names}) VALUES ({p})', values)
            assert cur.lastrowid is not None
            obj.pk = cur.lastrowid
        con.close()

        return obj.pk

    def get(self, pk: int) -> Any:
        """
        Получает объект по первичному ключу

        Параметры
        ----------
        pk - первичный ключ объекта


        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            row = cur.execute(f'SELECT * FROM {self.table_name} WHERE pk={pk}').fetchone()
        con.close()
        obj = self._row_to_obj(row)

        return obj

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получает все объекты таблицы базы данных. Есть возможность
        получить по условию. Для этого необходимо передать
        словарь, где ключ - название поля, значение - значение поля

        Параметры
        ----------
        where - условие


        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            sql = f'SELECT * FROM {self.table_name}'
            params = []
            if where is not None:
                for key, value in where.items():
                    params.append(value)
                fields = ' AND '.join([f'{key}=?' for key, value in where.items()])
                sql += " WHERE " + fields
            if where is not None:
                rows = cur.execute(sql, params).fetchall()
            else:
                rows = cur.execute(sql).fetchall()
        con.close()
        objs = [self._row_to_obj(rows[pk]) for pk in range(len(rows))]

        return objs

    def update(self, obj: T) -> None:
        """
        Обновление объекта таблицы в базе данных

        Параметры
        ----------
        obj - объект

        """
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        if obj.pk < 0:
            raise ValueError('attempt to update unexistent object')
        fields = ', '.join([f'{x}=?' for x in self.fields.keys()])
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'UPDATE {self.table_name} SET {fields} '
                        + f'WHERE pk={obj.pk}', values)
        con.close()

    def delete(self, pk: int) -> None:
        """
        Удаляет объект по ключу из таблицы базы данных

        Параметры
        ----------
        pk - первичный ключ объекта для удаления


        """
        if pk == 0:
            raise ValueError('attempt to delete object with unknown primary key')
        if pk < 0:
            raise ValueError('attempt to delete unexistent object')
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'DELETE FROM {self.table_name} WHERE pk={pk}')
        con.close()

    @classmethod
    def repo_factory(cls: type, models: list[type], db_file: str) -> dict[type, type]:
        """
        Возвращает репозитории нескольких моделей

        Параметры
        ----------
        models - модели для создания таблиц
        db_file - путь к базе данных

        """
        return {m: cls(db_file, m) for m in models}
