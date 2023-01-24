"""Builders to generate in memory representation of model and fields tree."""


from collections import defaultdict
from typing import Any, Dict, Optional, Set, List, cast

from . import errors
from .fields import NotSet, Value
from .types import (
    ClassValidator,
    JsonSchema,
    Model,
    Builder,
    SchemaPart,
    Field,
)


class BaseBuilder:
    def __init__(
        self,
        parent: Optional[Builder] = None,
        nullable: bool = False,
        default: Any = NotSet,
    ) -> None:
        self.parent = parent
        self.types_builders: Dict[Model, Builder] = {}
        self.types_count: Dict[Model, int] = defaultdict(int)
        self.definitions: Set[Builder] = set()
        self.nullable = nullable
        self.default = default

    @property
    def has_default(self) -> bool:
        return self.default is not NotSet

    def register_type(self, model_type: Model, builder: Builder) -> None:
        if self.parent:
            self.parent.register_type(model_type, builder)
            return

        self.types_count[model_type] += 1
        if model_type not in self.types_builders:
            self.types_builders[model_type] = builder

    def get_builder(self, model_type: Model) -> Builder:
        if self.parent:
            return self.parent.get_builder(model_type)

        return self.types_builders[model_type]

    def count_type(self, type: Model) -> int:
        if self.parent:
            return self.parent.count_type(type)

        return self.types_count[type]

    @staticmethod
    def maybe_build(value: Value) -> SchemaPart | Value:
        return value.build() if isinstance(value, Builder) else value

    def add_definition(self, builder: Builder) -> None:
        if self.parent:
            return self.parent.add_definition(builder)

        self.definitions.add(builder)


class ObjectBuilder(BaseBuilder):
    def __init__(self, model_type: Model, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.properties: Dict[str, JsonSchema] = {}
        self.required: List[str] = []
        self.model_type = model_type

        self.register_type(self.model_type, self)

    def add_field(self, name: str, field: Field, schema: JsonSchema) -> None:
        _apply_validators_modifications(schema, field)
        self.properties[name] = schema
        if field.required:
            self.required.append(name)

    def build(self) -> str | JsonSchema:
        builder = self.get_builder(self.model_type)
        if self.is_definition and not self.is_root:
            self.add_definition(builder)
            [self.maybe_build(value) for _, value in self.properties.items()]
            return f"#/definitions/{self.type_name}"
        else:
            return builder.build_definition(nullable=self.nullable)

    @property
    def type_name(self) -> str:
        module_name = f"{self.model_type.__module__}.{self.model_type.__name__}"
        return module_name.replace(".", "_").lower()

    def build_definition(
        self, add_defintitions: bool = True, nullable: bool = False
    ) -> JsonSchema:
        properties = {
            name: self.maybe_build(value) for name, value in self.properties.items()
        }
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": properties,
        }
        if self.required:
            schema["required"] = self.required
        if self.definitions and add_defintitions:
            schema["definitions"] = {
                builder.type_name: builder.build_definition(False, False)
                for builder in self.definitions
            }
        return schema

    @property
    def is_definition(self) -> bool:
        if self.count_type(self.model_type) > 1:
            return True
        elif self.parent:
            return self.parent.is_definition
        else:
            return False

    @property
    def is_root(self) -> bool:
        return not bool(self.parent)


def _apply_validators_modifications(field_schema: JsonSchema, field: Field) -> None:
    for validator in field.validators:
        if isinstance(validator, ClassValidator):
            validator.modify_schema(field_schema)

    if "items" in field_schema:
        for validator in field.item_validators:
            if isinstance(validator, ClassValidator):
                validator.modify_schema(field_schema["items"])


class PrimitiveBuilder(BaseBuilder):
    def __init__(self, value_type: type, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.value_type = value_type

    def build(self) -> JsonSchema:
        obj_type: list | str
        schema = {}
        if issubclass(self.value_type, str):
            obj_type = "string"
        elif issubclass(self.value_type, bool):
            obj_type = "boolean"
        elif issubclass(self.value_type, int):
            obj_type = "number"
        elif issubclass(self.value_type, float):
            obj_type = "number"
        elif issubclass(self.value_type, dict):
            obj_type = "object"
        else:
            raise errors.FieldNotSupported(
                "Can't specify value schema!", self.value_type
            )

        if self.nullable:
            obj_type = [obj_type, "null"]
        schema["type"] = obj_type

        if self.has_default:
            schema["default"] = self.default

        return schema


class ListBuilder(BaseBuilder):

    parent: Builder

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.schemas: list[JsonSchema] = []

    def add_type_schema(self, schema: JsonSchema) -> None:
        self.schemas.append(schema)

    def build(self) -> JsonSchema:
        schema: Dict[str, Any] = {"type": "array"}
        if self.nullable:
            self.add_type_schema({"type": "null"})

        if self.has_default:
            schema["default"] = [self.to_struct(i) for i in self.default]

        schemas = [self.maybe_build(s) for s in self.schemas]
        if len(schemas) == 1:
            items = schemas[0]
        else:
            items = {"oneOf": schemas}

        schema["items"] = items
        return schema

    @property
    def is_definition(self) -> bool:
        return self.parent.is_definition

    @staticmethod
    def to_struct(item: Value) -> Value:
        return item


class EmbeddedBuilder(BaseBuilder):
    parent: Builder

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.schemas: list[JsonSchema] = []

    def add_type_schema(self, schema: JsonSchema) -> None:
        self.schemas.append(schema)

    def build(self) -> JsonSchema:
        if self.nullable:
            self.add_type_schema({"type": "null"})

        schemas = cast(
            List[JsonSchema], [self.maybe_build(schema) for schema in self.schemas]
        )
        if len(schemas) == 1:
            schema = schemas[0]
        else:
            schema = {"oneOf": schemas}

        if self.has_default:
            # The default value of EmbeddedField is expected to be an instance
            # of a subclass of models.Base, thus have `to_struct`
            schema["default"] = self.default.to_struct()

        return schema

    @property
    def is_definition(self) -> bool:
        return self.parent.is_definition
