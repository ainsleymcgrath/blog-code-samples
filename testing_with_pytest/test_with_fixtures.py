from code_under_test import is_bread, is_bread_db

import pytest
from sqlite3 import Connection, connect

# the function under test
def is_bread(thing: str) -> bool:
    return thing == "bread"


# using this decorator 'registers' the function as a fixture
@pytest.fixture
def non_bread() -> str:
    return "friendship"


# when a test function has an argument with the same name as some fixture,
# it 'requests' the fixture's return value for use
def test_is_bread(non_bread):
    assert (
        is_bread(non_bread) is False
    ), "When passed a non-bread function returns False"


@pytest.fixture
def testconn() -> Connection:
    # this is setup
    connection = connect(":memory:")
    # table with 2 columns
    connection.execute("create table things (name text, is_bread bool);")
    # a few preexisting records
    connection.executemany(
        "insert into things values (?,?)",
        [("bread", True), ("mirth", False), ("croissant", True)],
    )

    # this is dependency provisioning
    yield connection

    # this is teardown
    connection.execute("drop table things")
    connection.close()


def test_is_bread_db(testconn: Connection):
    assert is_bread_db(testconn, "bread") is True, "Bread is bread"
    assert is_bread_db(testconn, "mirth") is False, "Mirth is not bread"
