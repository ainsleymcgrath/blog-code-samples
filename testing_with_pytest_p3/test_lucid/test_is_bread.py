from ..testing import CrudCase, CrudCaseArtifact, ThingSeeder
from ..crud import NoRecordFoundError, augment_thing_by_name, is_bread

f = ThingSeeder.factory

seed_data = [
    f(name="poison", is_bread=False, type="substance", origin="unknown", rating=0),
    f(name="banana", is_bread=False, type="food", origin="malay archipelago", rating=4),
    f(name="miche", is_bread=True, type="food", origin="france", rating=5),
]

table = [
    CrudCase(args=("poison",), assert_return=False, should="Poison is not bread"),
    CrudCase(args=("miche",), assert_return=True, should="Miche is excellent bread"),
    CrudCase(
        args=("uh oh",),
        seed_data=[],
        raises=NoRecordFoundError,
        should="Raise for missing stuff",
        func=is_bread,
    ),
    CrudCase(
        func=augment_thing_by_name,
        kwargs={"name": "poison", "field": "rating", "value": 2},
        should="Update the rating of bananas",
        assert_return=CrudCase.SKIPCHECK,
    ),
]


def test(crud_case: CrudCaseArtifact):
    if crud_case.case.func is augment_thing_by_name:
        assert crud_case.actual_result.rating == 2
