def is_bread(thing: str) -> bool:
    """Predicate: Determine if incoming `thing` is bread."""
    return thing == "bread"


from sqlite3 import Connection


def is_bread_db(connection: Connection, thing_name: str) -> bool:
    """Predicate: Check record in the 'things' table to see if its bread."""
    cursor = connection.execute(
        # in sqlite, `?` is used as a placeholder
        "select is_bread from things where name = ?",
        (thing_name,),
    )
    (result,) = cursor.fetchone()
    return result == 1  # sqlite uses 1/0 for True/False
