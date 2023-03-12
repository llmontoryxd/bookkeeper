import sqlite3
from inspect import get_annotations
from typing import Any
from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls
        self.create_table()

    def _row_to_obj(self, row: tuple[Any] | None) -> Any:
        if row is None:
            return None
        obj = self.cls(**dict(zip({'pk': int} | self.fields, row)))

        return obj

    def create_table(self) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name}('
                        + 'pk INTEGER PRIMARY KEY, '
                        + ', '.join(self.fields.keys()) + ')')
        con.close()

    def drop_table(self) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'DROP TABLE IF EXISTS {self.table_name}')
        con.close()

    def add(self, obj: T) -> int:
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
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            row = cur.execute(f'SELECT * FROM {self.table_name} WHERE pk={pk}').fetchone()
        con.close()
        obj = self._row_to_obj(row)

        return obj

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
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
        return {m: cls(db_file, m) for m in models}
