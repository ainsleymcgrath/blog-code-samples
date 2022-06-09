from ..testing import CrudCase, ThingSeeder as seed
from ..crud import NoRecordFoundError

seed_data = [
    seed.factory(
        name="poison", is_bread=False, type="substance", origin="unknown", rating=0
    ),
    seed.factory(
        name="banana", is_bread=False, type="food", origin="malay archipelago", rating=4
    ),
    seed.factory(name="miche", is_bread=True, type="food", origin="france", rating=5),
]

table = [
    CrudCase(args=("poison",), assert_return=False, should="Poison is not bread"),
    CrudCase(args=("miche",), assert_return=True, should="Miche is excellent bread"),
    CrudCase(
        args=("uh oh",),
        seed_data=[],
        raises=NoRecordFoundError,
        should="Raise for missing stuff",
    ),
]


def test(crud_case):
    ...
