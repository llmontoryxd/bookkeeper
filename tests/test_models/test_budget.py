import pytest

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_with_full_args_list():
    b = Budget(pk=1, amount=10.1, budget=13.1)
    assert b.amount == 10.1
    assert b.budget == 13.1


def test_create_brief():
    b = Budget(10.1, 13.1)
    assert b.amount == 10.1
    assert b.budget == 13.1


def test_can_add_to_repo(repo):
    b = Budget(10.1, 13.1)
    pk = repo.add(b)
    assert b.pk == pk
