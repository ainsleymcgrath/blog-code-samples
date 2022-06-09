import pytest
from . import crud
from .testing import ThingSeeder


@pytest.fixture(autouse=True)
def seed(seeder: ThingSeeder):
    records = (
        ("bread", True, "food", "bakery", 5),
        ("mirth", False, "feeling", "prefontal cortex", 5),
        ("fear", False, "feeling", "prefontal cortex", 0),
        ("croissant", True, "food", "france", 4),
        ("spork", False, "utensil", "unknown", 2),
        ("fish spatula", False, "utensil", "switzerland", 5),
    )
    seeder.seed(
        seeder.factory(
            name=name, is_bread=is_bread, type=type, origin=origin, rating=rating
        )
        for name, is_bread, type, origin, rating in records
    )


def test_is_bread(testconn):
    result = crud.is_bread(testconn, "croissant")
    assert result is True, "A croissant is bread"


def test_count_of_thing_origin(testconn):
    result = crud.count_of_thing_origin(testconn, "prefontal cortex")
    assert result == 2, "Two things originate from the prefontal cortex"


def test_get_one_thing(testconn):
    result = crud.get_one_thing(testconn, "spork")
    assert result.name == "spork", "Things can be retrieved by name"


def test_get_all_rated_below(testconn):
    result = crud.get_all_rated_below(testconn, "3")
    assert len(result) == 2
    assert [r.name for r in result] == ["fear", "spork"]


def test_save_thing(testconn):
    thing = crud.Thing(
        name="macbook",
        is_bread=False,
        type="technology",
        origin="cupertino",
        rating=4,
    )
    crud.save_thing(testconn, thing)

    cursor = testconn.execute("select count(*) = 1 from things where name = 'macbook'")
    (result,) = cursor.fetchone()
    assert result == 1


def test_augment_thing_by_name(testconn):
    updated_thing = crud.augment_thing_by_name(
        testconn, name="fear", field="rating", value=2
    )
    assert updated_thing.rating == 2


def test_never_more_than_n_of_type(testconn):
    with pytest.raises(crud.TooManyRecordsOfThingTypeError):
        crud.never_more_than_n_of_type(testconn, "feeling", n=1)

    try:
        crud.never_more_than_n_of_type(testconn, "feeling", n=2)
    except crud.TooManyRecordsOfThingTypeError:
        pytest.fail("There are not more than 2 things")


def test_stupildy_check_uniqueness_client_side(testconn):
    try:
        crud.stupidly_check_uniqueness_client_side(testconn)
    except crud.StupidUniqueConstraintError:
        pytest.fail("Everything is unique.")

    crud.save_thing(
        testconn,
        crud.Thing(
            name="croissant", is_bread=True, type="food", origin="france", rating=5
        ),
    )
    with pytest.raises(crud.StupidUniqueConstraintError):
        crud.stupidly_check_uniqueness_client_side(testconn)
