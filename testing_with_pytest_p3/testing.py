import re
from importlib import import_module
from dataclasses import dataclass, field, fields
from sqlite3 import Connection
from typing import Any, ClassVar, Protocol, Type


class CrudFunc(Protocol):
    __name__: str

    def __call__(self, connection: Connection, *args: Any, **kwargs: Any):
        ...


@dataclass
class CrudCase:
    should: str
    assert_return: Any
    func: CrudFunc | None = None

    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    raises: Type[Exception] | None = None
    assert_sql: list[str] = field(default_factory=list)
    seed_data: list[tuple] = field(default_factory=list)
    table: list["CrudCase"] = field(default_factory=list)

    TEST_MODULE_NAME_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"test_(?P<func_name>\w.*)"
    )

    def call(self) -> Any:
        if self.func is None:
            raise TypeError("No func given :/")
        return self.func(*self.args, *self.kwargs)

    @classmethod
    def from_module(
        cls, module: Any, func_location: str = "testing_with_pytest_p3.crud"
    ) -> "CrudCase":
        kwargs = {
            f.name: getattr(module, f.name)
            for f in fields(cls)
            if f.name in dir(module)
        }

        if "should" not in kwargs:
            kwargs["should"] = module.__doc__

        if "assert_return" not in kwargs:
            kwargs["assert_return"] = None

        if "func" not in kwargs:
            *_, stem = module.__name__.split(".")
            match = cls.TEST_MODULE_NAME_PATTERN.search(stem)
            if match is None:
                raise AttributeError
            func_name = match.group("func_name")
            kwargs["func"] = getattr(import_module(func_location), func_name)

        return cls(**kwargs)

    def testid(self) -> str:
        assert self.func is not None
        return f"{self.func.__name__}() -> {self.should}"


@dataclass
class CrudCaseArtifact:
    case: CrudCase
    actual_result: Any


@dataclass
class ThingSeeder:
    conn: Connection

    def seed(self, records):
        self.conn.executemany("insert into things values (?,?,?,?,?)", [*records])

    @staticmethod
    def factory(*, name, is_bread, type, origin, rating):
        return name, is_bread, type, origin, rating
