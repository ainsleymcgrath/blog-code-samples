import pytest
from sqlite3 import Connection, connect
from typing import Callable

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


CaseRunner = Callable[[CrudCase], CrudCaseArtifact]


@pytest.fixture
def run_crud_case(seeder: ThingSeeder, testconn: Connection):
    def run(case: CrudCase) -> CrudCaseArtifact:
        artifact = CrudCaseArtifact(case=case)
        seeder.seed(case.seed_data)

        if (exc := case.raises) is not None:
            with pytest.raises(exc):
                case.call()
        else:
            actual_result = case.call()
            artifact.actual_result = actual_result
            if not case.assert_return is case.SKIPCHECK:
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
        return artifact

    return run


@pytest.fixture
def crud_case(
    run_crud_case: CaseRunner, testconn: Connection, case: CrudCase
) -> CrudCaseArtifact:
    """When requested, this fixture inspects the requesting module and generates
    tests accordingly."""
    case.args = (testconn, *case.args)
    return run_crud_case(case)


def pytest_generate_tests(metafunc: pytest.Metafunc):
    if "crud_case" in metafunc.fixturenames:
        root_case = CrudCase.from_module(metafunc.module)

        if root_case.table == []:
            metafunc.parametrize("case", [root_case], ids=[root_case.testid()])
            return

        module_seed_data = getattr(metafunc.module, "seed_data", [])
        for case in root_case.table:
            if case.seed_data == []:
                case.seed_data = module_seed_data

            if case.func is None:
                case.func = root_case.func

        cases = root_case.table if root_case.table != [] else [root_case]
        metafunc.parametrize("case", cases, ids=[c.testid() for c in cases])
