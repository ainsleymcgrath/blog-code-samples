import pytest
from sqlite3 import Connection, connect

from .testing import CrudCase, CrudCaseArtifact, ThingSeeder

# fixtures can do much more than provide primitive values
@pytest.fixture
def testconn():
    connection = connect(":memory:")
    connection.execute(
        """
        create table things
        (
            name text,
            is_bread bool,
            type text,
            origin text,
            rating int
        );"""
    )

    yield connection

    connection.execute("drop table things")
    connection.close()


@pytest.fixture
def seeder(testconn: Connection):
    return ThingSeeder(testconn)


@pytest.fixture
def run_crud_case(seeder: ThingSeeder, testconn: Connection):
    def run(case: CrudCase):
        seeder.seed(case.seed_data)

        if (exc := case.raises) is not None:
            with pytest.raises(exc):
                case.call()
        else:
            actual_result = case.call()
            assert case.assert_return == actual_result, case.should

        for assertion_query in case.assert_sql:
            cursor = testconn.execute(assertion_query)
            try:
                (only_result,) = cursor.fetchone()
            except (TypeError, ValueError):
                pytest.fail(
                    f"SQL assertion for {case} did not return 1 row with 1 boolean column"
                )

            assert only_result == 1, f"{assertion_query} returns `true`"

    return run


@pytest.fixture
def crud_case(run_crud_case, testconn: Connection, case: CrudCase):
    """When requested, this fixture inspects the requesting module and generates
    tests accordingly."""
    case.args = (testconn, *case.args)
    result = run_crud_case(case)
    return CrudCaseArtifact(actual_result=result, case=case)


def pytest_generate_tests(metafunc: pytest.Metafunc):
    if "crud_case" in metafunc.fixturenames:
        parent_case = CrudCase.from_module(metafunc.module)
        module_seed_data = getattr(metafunc.module, "seed_data", [])
        for case in parent_case.table:
            if case.seed_data == []:
                case.seed_data = module_seed_data

            if case.func is None:
                case.func = parent_case.func

        cases = parent_case.table if parent_case.table != [] else [parent_case]
        metafunc.parametrize("case", cases, ids=[c.testid() for c in cases])
