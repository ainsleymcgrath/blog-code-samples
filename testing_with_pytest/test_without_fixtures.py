from code_under_test import is_bread


def test_is_bread():
    thing = "satisfaction"
    result = is_bread(thing)

    assert result is False, "When passed a non-bread function returns False"
