from typing import Any, Callable, Dict, List, Protocol, Tuple, runtime_checkable

Value = Any
JsonSchema = Dict[str, Any]
SchemaPart = str | dict


@runtime_checkable
class Builder(Protocol):
    def register_type(self, type: "Model", builder: "Builder") -> None:
        ...

    def get_builder(self, model_type: "Model") -> "Builder":
        ...

    def count_type(self, type: "Model") -> int:
        ...

    def build(self) -> SchemaPart:
        ...

    def add_definition(self, builder: "Builder") -> None:
        ...

    def build_definition(self, add_defintitions=True, nullable=False) -> JsonSchema:
        ...

    @property
    def type_name(self) -> str:
        ...

    @property
    def is_definition(self) -> bool:
        ...


@runtime_checkable
class ClassValidator(Protocol):
    def modify_schema(self, field_schema: JsonSchema) -> None:
        ...


Validator = Callable | ClassValidator


class Model(Protocol):

    __name__: str


class Field(Protocol):

    required: bool = False
    validators: List[Validator]
    item_validators: List[Validator]


Fields = Tuple[str, Field]
FieldsWithNames = Tuple[str, str, Field]
