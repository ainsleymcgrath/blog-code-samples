from dataclasses import dataclass
from sqlite3 import Connection, Row
from typing import Any


def is_bread(conn: Connection, thing_name: str) -> bool:
    cursor = conn.execute(
        # in sqlite, `?` is used as a placeholder
        "select is_bread from things where name = ?",
        (thing_name,),
    )
    (result,) = cursor.fetchone()
    return result == 1  # sqlite uses 1/0 for True/False


def count_of_thing_origin(conn: Connection, origin: str) -> int:
    cursor = conn.execute(
        "select count(*) from things where origin = ?",
        (origin,),
    )
    (result,) = cursor.fetchone()
    return result


@dataclass
class Thing:
    name: str
    is_bread: bool
    type: str
    origin: str
    rating: int


def get_one_thing(conn: Connection, name: str) -> Thing:
    conn.row_factory = Row
    cursor = conn.execute("select * from things where name = ?", (name,))
    result = cursor.fetchone()
    return Thing(**result)


def get_all_rated_below(conn: Connection, rating: int) -> list[Thing]:
    conn.row_factory = Row
    cursor = conn.execute(
        "select * from things where rating < ? order by name",
        (rating,),
    )
    results = cursor.fetchall()
    return [Thing(**r) for r in results]


def save_thing(conn: Connection, thing: Thing) -> None:
    conn.execute(
        f"""insert into things (name, is_bread, type, origin, rating)
        values (?, ?, ?, ?, ?)""",
        [thing.name, thing.is_bread, thing.type, thing.origin, thing.rating],
    )


def augment_thing_by_name(
    conn: Connection, *, name: str, field: str, value: Any
) -> Thing:
    conn.row_factory = Row
    conn.execute(
        f"""
        update things set {field} = ?
        where name = ?
        """,
        (value, name),
    )
    augmented = conn.execute("select * from things where name = ?", (name,)).fetchone()
    return Thing(**augmented)


class TooManyRecordsOfThingTypeError(Exception):
    ...


def never_more_than_n_of_type(conn: Connection, type: str, *, n) -> None:
    cursor = conn.execute(
        "select count(*) from things where type = ?",
        (type,),
    )
    (result,) = cursor.fetchone()
    if result > n:
        raise TooManyRecordsOfThingTypeError(
            f"Can't have more than {n} of type={type}. Found {result}."
        )


class StupidUniqueConstraintError(Exception):
    """You'd better do this server side in real life."""


def stupidly_check_uniqueness_client_side(conn: Connection) -> None:
    cursor = conn.execute(
        """select 
            (select count(*) from things)
            = (select count(distinct name) from things)"""
    )
    (result,) = cursor.fetchone()
    if result == 0:
        raise StupidUniqueConstraintError("Your cLiEnT sIdE iNtEgRiTy cHeCk failed.")
