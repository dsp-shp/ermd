from __future__ import annotations
from collections import UserDict
from dataclasses import dataclass
from enum import Enum
from functools import reduce
from pathlib import Path
import typing as t
import re


class DataType(Enum):
    ...

class EntityFieldKey(Enum):
    """ Type of entity attribute's key """
    PRIMARY = "PK"
    FOREIGN = "FK"

class RelationType(Enum):
    """ One-side relation """
    ZERO = "0"
    ONE = "1"
    ZERO_OR_ONE = "0..1"
    MANY = "M"
    ZERO_OR_MANY = "0..M"
    ONE_OR_MANY = "1..M"


# @dataclass
class EntityField:
    """ Entity attribute """

    def __init__(
        self,
        entity: Entity,
        name: str,
        key: t.Optional[EntityFieldKey] = None,
        data_type: t.Optional[str] = None,
        desc: t.Optional[str] = None,
        relation: t.Optional[Relation] = None,
    ) -> None:
        self.entity = entity
        self.name = name
        self.key = key
        self.data_type = data_type
        self.desc = desc
        self.relation = relation

    @property
    def __dict__(self) -> dict[str, t.Any]: # type: ignore
        return {
            "name": self.name,
            "key": self.key.value if self.key else None,
            "data_type": self.data_type,
            "desc": self.desc
        }

    @classmethod
    def from_string(cls, entity: Entity, s: str, exist_ok: bool = False) -> t.Self:
        """
        Parse entity field from a string.
        """
        _s = s[:]
        _s = re.sub(r"^[\t\ ]*\-", "", _s)

        keys = []
        for x in reversed([*re.finditer(r"\[.+?\]", _s)]):
            if len(keys) > 1:
                raise ValueError("for now only one key can be provided for a field")
            keys.append(EntityFieldKey(x.group().strip("[ ]").upper()))
            _s = _s[:x.start()] + _s[x.end():]

        descs = []
        for x in reversed([*re.finditer(r'\".+?\"', _s)]):
            if len(descs) > 1:
                raise ValueError("only one description can be provided for a field")
            descs.append(x.group().strip('"'))
            _s = _s[:x.start()] + _s[x.end():]

        data_types = []
        for x in reversed([*re.finditer(r'@[a-z|A-Z]+', _s)]):
            if len(data_types) > 1:
                raise ValueError("only one data type can be provided for a field")
            data_types.append(x.group().strip('@'))
            _s = _s[:x.start()] + _s[x.end():]

        name = _s.split("---")[0].strip(" ").lower()
        if name in entity.data:
            if not exist_ok:
                raise ValueError(f"field \"{name}\" of \"{entity.name}\" already exists")
            else:
                return entity.data[name]

        global relations
        for x in reversed([*re.finditer(r'\-\-\-[^ \n]+?---[^ \n]+', _s)]):
            if len(relations) > 1:
                raise ValueError(f"for now only one relation can be provided for a field \"{name}\"")
            relations.append(f"{entity.name}.{name}{x.group().strip()}")
            _s = _s[:x.start()] + _s[x.end():]

        return cls(
            entity,
            name,
            key = [*keys, None][0],
            data_type = [*data_types, None][0],
            desc = [*descs, None][0]
        ) # type: ignore


class Entity(UserDict):
    """ Entity """

    def __init__(
        self,
        name: str,
        data: t.Optional[dict[str, EntityField]] = None,
        desc: t.Optional[str] = None
    ) -> None:
        self.name = name.strip().lower()
        self.desc = desc.strip(' "') if desc else None
        self.data = {}

    @property
    def __dict__(self) -> dict[str, t.Any]: # type: ignore
        return {k: dict(v) for k, v in self.data.items()}

    def _add_field(self, s: str, exist_ok: bool = False) -> EntityField:
        field = EntityField.from_string(self, s, exist_ok=exist_ok)
        self.data[field.name] = field
        return field

    @classmethod
    def from_string(cls, s: str) -> t.Self:
        """
        Create an entity from a string. At first initialize empty
        entity object and then add fields to it.
        """
        name_and_desc, *fields_listed = s.splitlines()
        name, desc = name_and_desc.strip("\" ").split("\"", 1) + [None]
        entity = cls(name, desc = desc) # type: ignore

        # Add fields
        for x in fields_listed:
            field = EntityField.from_string(entity, x)
            entity.data[field.name] = field

        return entity


class Relation:
    def __init__(
        self,
        from_field: EntityField,
        to_field: EntityField,
        from_type: RelationType,
        to_type: RelationType,
        from_desc: t.Optional[str] = None,
        to_desc: t.Optional[str] = None
    ) -> None:
        self.from_field = from_field
        self.to_field = to_field
        self.from_type = from_type
        self.to_type = to_type
        self.from_desc = from_desc
        self.to_desc = to_desc

    def __str__(self) -> str:
        return "{0}.{1}---{2}{3}:{6}{7}---{4}.{5}".format(
            *reduce(
                lambda a, b: a + b,
                sorted([(
                    self.from_field.entity.name,
                    self.from_field.name,
                    self.from_type.value,
                    self.from_desc or ""
                ), (
                    self.to_field.entity.name,
                    self.to_field.name,
                    self.to_type.value,
                    self.to_desc or ""
                )
            ], key=lambda x: (x[0], x[1])))
        ).replace("()", "")

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other) -> bool:
        return hash(self) == hash(other)

    def __neg__(self) -> Relation:
        """
        Return inverted relation where left and right fields are swapped.
        """
        return Relation(
            from_field=self.to_field,
            to_field=self.from_field,
            from_type=self.to_type,
            to_type=self.from_type,
            from_desc=self.to_desc,
            to_desc=self.from_desc
        )

    @property
    def __dict__(self) -> dict[str, t.Any]:
        return {}

    @classmethod
    def from_string(cls, s: str) -> t.Self:
        global entries
        from_full, rel, to_full = s.strip("").split("---")
        from_entity, from_field = from_full.strip().lower().split(".")
        to_entity, to_field = to_full.strip().lower().split(".")

        # Try find entity and field and create ones if missing
        if from_entity not in entities:
            entities[from_entity] = Entity(from_entity)
        from_field = entities[from_entity]._add_field(f"- {from_field}", exist_ok=True)
        if to_entity not in entities:
            entities[to_entity] = Entity(to_entity)
        to_field = entities[to_entity]._add_field(f"- {to_field}", exist_ok=True)

        from_desc, to_desc, *_ = re.findall(r"\(.+?\)", rel) + [None, None]
        rel = re.sub(r"\(.+?\)", "", rel).strip()
        from_type, to_type = [RelationType(x.upper()) for x in rel.split(":")]

        rel = cls(
            from_field,
            to_field,
            from_type,
            to_type,
            from_desc,
            to_desc
        ) # type: ignore
        from_field.relation, to_field.relation = rel, -rel

        return rel


s = Path("README.md").read_text()
print(s)

# Clear all comments with finditer, re.sub doesn't work idkw
for x in reversed([*re.finditer(r"<!--.+?-->", s, re.MULTILINE | re.DOTALL)]):
    start, end = x.span()
    s = s[:start] + s[end:]
s = s.strip("\t\n ")

re.findall(r"(?m)^([A-Za-z]+\n(?:- .+\n)+)", s, re.MULTILINE)[1]

# Get global statements: that could be either entity definition or relation
relations = re.findall(r".+\..+---.+---.+\..+", s, re.MULTILINE)
entities: dict[str, Entity] = {}
for x in re.findall(r"(?m)^([A-Za-z]+\n(?:- .+\n)+)", s, re.MULTILINE):
    y = Entity.from_string(x)
    if y.name in entities:
        raise ValueError(f"Duplicate entity name: {y.name}")
    entities[y.name] = y

entities["regions"]

[Relation.from_string(x) for x in relations]

entities["customers"]._add_field("- gender_id", exist_ok=True)
entities["customers"]["gender_id"].relation == entities["genders"]["id"].relation
