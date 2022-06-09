"""Create exactly one record."""
from ..crud import Thing

args = (
    Thing(
        name="macbook",
        is_bread=False,
        type="technology",
        origin="cupertino",
        rating=4,
    ),
)
assert_return = None
assert_sql = ["select count(*) = 1 from things where name = 'macbook'"]


def test(crud_case):
    ...
