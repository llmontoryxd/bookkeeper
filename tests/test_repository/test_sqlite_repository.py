import pytest
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from dataclasses import dataclass

DB_FILE = 'test.db'


@pytest.fixture
def custom_class():
    @dataclass
    class Custom:
        pk: int = 0
        f1: int = 1
        f2: str = 'value'
        f3: float = 1.1
    return Custom


@pytest.fixture
def repos(custom_class):
    repos = SQLiteRepository.repo_factory(db_file=DB_FILE, models=[custom_class])
    yield repos
    for cls, repo in repos.items():
        repo.drop_table()


@pytest.fixture
def repo(repos, custom_class):
    return repos[custom_class]


def test_crud(repo, custom_class):
    obj = custom_class(f1=2, f2='custom value', f3=1.2)
    pk = repo.add(obj)
    assert pk == obj.pk
    assert repo.get(pk) == obj
    obj2 = custom_class()
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) is None


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class(pk=1)
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_update_unexistent(repo, custom_class):
    obj = custom_class(pk=-1)
    with pytest.raises(ValueError):
        repo.update(obj)


def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)


def test_cannot_get_unexistent(repo):
    assert repo.get(-1) is None


def test_cannot_delete_unexistent(repo):
    with pytest.raises(ValueError):
        repo.delete(-1)


def test_cannot_delete_without_pk(repo):
    with pytest.raises(ValueError):
        repo.delete(0)


def test_get_all(repo, custom_class):
    objects = [custom_class(f1=i) for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects


def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class(f1=1)
        o.f1 = i
        o.f2 = 'test value'
        repo.add(o)
        objects.append(o)
    assert repo.get_all({'f1': 0}) == [objects[0]]
    assert repo.get_all({'f2': 'test value'}) == objects


def test_row_to_obj(repo):
    row = (1, 2, 'test value')
    obj = repo._row_to_obj(row)
    assert obj.f1 == 2
    assert obj.f2 == 'test value'



