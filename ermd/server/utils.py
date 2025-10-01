from __future__ import annotations
from collections import UserDict
from enum import Enum
from functools import reduce
from pathlib import Path

import logging
import typing as t
import re


logger = logging.getLogger(__name__)


entities: dict[str, Entity] = {}
""" Finally formed entities """

relations: list[Relation] = []
""" Finally formed relations """

relations_raw: list[str] = []
""" List of relation strings found during entity creation to parse after """


class EntityFieldKey(Enum):
    """ Type of entity attribute's key """
    PRIMARY = "PK"
    FOREIGN = "FK"
    # Add support for FK1/2/3/...


class EntityType(Enum):
    """ Type of entity """
    TABLE = "TABLE"
    VIEW = "VIEW"
    MATVIEW = "MATVIEW"


class RelationType(Enum):
    """ One-side relation """
    ZERO = "0"
    ONE = "1"
    ZERO_OR_ONE = "0..1"
    MANY = "M"
    ZERO_OR_MANY = "0..M"
    ONE_OR_MANY = "1..M"


class EntityField:
    """ Entity attribute """

    def __init__(
        self,
        entity: Entity,
        name: str,
        id: t.Optional[int] = None,
        keys: t.Optional[set[EntityFieldKey]] = None,
        data_type: t.Optional[str] = None,
        desc: t.Optional[str] = None,
        relations: t.Optional[list[Relation]] = None,
    ) -> None:
        self.entity = entity
        self.name = name
        self.id = id
        self.keys = keys or set()
        self.data_type = data_type
        self.desc = desc
        self.relations = relations or []

    @classmethod
    def from_string(cls, entity: Entity, s: str, exist_ok: bool = False) -> t.Self:
        """
        Parse entity field from a string.
        """
        _s = s[:]
        _s = re.sub(r"^[\t\ ]*\-", "", _s)

        keys = set()
        for x in reversed([*re.finditer(r"\[.+?\]", _s)]):
            keys.add(EntityFieldKey(x.group().strip("[ ]").upper()))
            _s = _s[:x.start()] + _s[x.end():]

        _relations_raw = []
        for x in reversed([*re.finditer(r'---.+?---[^\ \n]+', _s)]):
            _relations_raw.append(x.group().strip())
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

        _relations = [f"{entity.name}.{name}{x}" for x in _relations_raw]
        if _relations:
            global relations_raw
            relations_raw += _relations

        return cls(
            entity,
            name,
            keys = keys,
            data_type = [*data_types, None][0],
            desc = [*descs, None][0]
        ) # type: ignore

    def to_dict(self) -> dict[str, t.Any]:
        # Side to move from root node to leaves
        side = self.entity.side or "right"
        if self.entity.level != 0:
            from_type = ([x.from_type for x in self.relations if x.to_field.entity.level > self.entity.level] + [None])[0]
            to_type = ([x.from_type for x in self.relations if x.to_field.entity.level < self.entity.level] + [None])[0]
            l_type, r_type = (to_type, from_type)[::(1 if side == "right" else -1)]
        else:
            l_type, r_type = None, None
            _type = self.relations[0].from_type if self.relations else None
            if self.id != None and self.id % 2 == 0:
                l_type = _type
            else:
                r_type = _type

        d = {
            "name": self.name,
            "keys": list(sorted(self.keys, key=lambda x: ("PK", "FK").index(x.value))),
            "data_type": self.data_type,
            "desc": self.desc,
            "l_type": l_type,
            "r_type": r_type
        }
        return d

    def findall(
        self,
        side: str,
        entities: list[Entity] = [],
        root: t.Optional[Entity] = None,
        level: int = 0
    ) -> list[Entity]:
        if not root:
            level = 0
            root = self.entity
            self.entity.level = level
            entities = []
        if self.relations:
            for r in self.relations:
                if r.to_field.entity not in [*entities, root]:
                    r.to_field.entity.root = root
                    r.to_field.entity.parent = self.entity
                    r.to_field.entity.side = side
                    r.to_field.entity.level = level + 1
                    entities.append(r.to_field.entity)
                    for x in r.to_field.entity.data.values():
                        entities += x.findall(side, entities, root, level+1)
        return entities


class Entity(UserDict):
    """ Entity """

    def __init__(
        self,
        name: str,
        data: t.Optional[dict[str, EntityField]] = None,
        side: t.Optional[str] = None,
        entity_type: t.Optional[str] = None,
        desc: t.Optional[str] = None,
    ) -> None:
        self.name = name.strip().lower()
        self.desc = desc.strip(' "') if desc else None
        self.entity_type = EntityType(entity_type.strip().upper()) if entity_type else None
        self.data = {}

        # Following attributes can be set only within order_relations
        self.side = None
        self.level = 0
        self.root = None
        self.parent = None

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def relations(self) -> list[Relation]:
        grouped_relations = [x.relations for x in self.data.values() if x.relations]
        if not self.data or not grouped_relations:
            return []
        return reduce(lambda a,b: a+b, [x.relations for x in self.data.values()])

    def _add_field(self, s: str, exist_ok: bool = False) -> EntityField:
        field = EntityField.from_string(self, s, exist_ok=exist_ok)
        if field.name in self.data:
            field.id = list(self.data).index(field.name)
        else:
            field.id = len(self.data)
        self.data[field.name] = field
        return field

    @classmethod
    def from_string(cls, s: str) -> t.Self:
        """
        Create an entity from a string. At first initialize empty
        entity object and then add fields to it.
        """
        name_and_desc, *fields_listed = s.splitlines()

        entity_types = []
        for x in reversed([*re.finditer(r'@[a-z|A-Z]+', name_and_desc)]):
            if len(entity_types) > 1:
                raise ValueError("only one entity type can be provided")
            entity_types.append(x.group().strip('@'))
            name_and_desc = name_and_desc[:x.start()] + name_and_desc[x.end():]
        entity_types += ["TABLE"]

        name_and_desc = re.sub(r"[\ ]+", " ", name_and_desc)
        name, desc, *_ = name_and_desc.strip("\" ").split("\"", 1) + [None, None]
        entity = cls(name, entity_type=entity_types[0], desc=desc) # type: ignore

        # Add fields
        for i, x in enumerate(fields_listed):
            field = EntityField.from_string(entity, x)
            field.id = i
            entity.data[field.name] = field

        return entity

    def to_dict(self) -> dict[str, t.Any]:
        d = {
            "name": self.name,
            "desc": self.desc,
            "type": self.entity_type.value if self.entity_type else "UNDEFINED",
            "fields": [v.to_dict() for k, v in self.data.items()],
            "level": self.level,
            "side": self.side
        }
        return d


class Relation:
    def __init__(
        self,
        from_field: EntityField,
        to_field: EntityField,
        from_type: RelationType,
        to_type: RelationType,
        desc: t.Optional[str] = None
    ) -> None:
        self.from_field = from_field
        self.to_field = to_field
        self.from_type = from_type
        self.to_type = to_type
        self.desc = desc

    def __str__(self) -> str:
        return "{0}.{1}---{2}{3}:{6}{7}---{4}.{5}".format(
            *reduce(
                lambda a, b: a + b,
                sorted([(
                    self.from_field.entity.name,
                    self.from_field.name,
                    self.from_type.value,
                    self.desc or ""
                ), (
                    self.to_field.entity.name,
                    self.to_field.name,
                    self.to_type.value,
                    self.desc or ""
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
            desc=self.desc,
        )

    @classmethod
    def from_string(cls, s: str) -> t.Self:
        global entities

        from_full, rel, to_full = s.strip("").split("---")
        rel = rel.strip("( )")
        from_entity, from_field = from_full.strip().lower().split(".")
        to_entity, to_field = to_full.strip().lower().split(".")

        # Try find entity and field and create ones if missing
        if from_entity not in entities:
            entities[from_entity] = Entity(from_entity)
        from_field = entities[from_entity]._add_field(f"- {from_field}", exist_ok=True)
        if to_entity not in entities:
            entities[to_entity] = Entity(to_entity)
        to_field = entities[to_entity]._add_field(f"- {to_field}", exist_ok=True)

        # Make keys of these fields foreign
        from_field.keys.add(EntityFieldKey("FK"))
        to_field.keys.add(EntityFieldKey("FK"))

        rel, desc, *_ = re.sub(r"\s+", " ", rel).split(" ", 1) + [None, None]
        if desc:
            desc = desc.strip('"')

        from_type, to_type, *_ = [RelationType(x.upper()) for x in rel.split(":")]

        rel = cls(
            from_field,
            to_field,
            from_type,
            to_type,
            desc if desc else None,
        ) # type: ignore
        if hash(rel) not in [hash(x) for x in from_field.relations]:
            from_field.relations.append(rel)
        if hash(rel) not in [hash(x) for x in to_field.relations]:
            to_field.relations.append(-rel)

        return rel

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "from": f"{self.from_field.entity.name}.{self.from_field.name}",
            "from_type": self.from_type.value,
            "desc": self.desc,
            "to": f"{self.to_field.entity.name}.{self.to_field.name}",
            "to_type": self.to_type.value,
        }


def order_relations() -> dict[str, t.Any]:
    global entities
    global relations

    map_entities = {x: [
        (y if y.from_field.entity == x else -y) for y in x.relations
    ] for x in entities.values()}

    map_entities = dict(sorted(map_entities.items(), key=lambda x: len(x[1]), reverse=True))

    left = set()
    right = set()

    res_relations = {}
    for e in map_entities:
        if hasattr(e, "level") and e.level:
            continue
        for y in map_entities[e]:
            if y.from_field.id % 2 == 0:
                left.update(y.from_field.findall("left"))
                res_relations[hash(y)] = -y
            else:
                right.update(y.from_field.findall("right"))
                res_relations[hash(y)] = y

    left = sorted(left, key=lambda x: x.level, reverse=True)
    right = sorted(right, key=lambda x: x.level, reverse=False)
    for x in [*left, *right]:
        for y in map_entities[x]:
            if hash(y) not in res_relations:
                res_relations[hash(y)] = (y)

    for x in [x for x in relations if hash(x) not in res_relations]:
        res_relations[hash(x)] = x

    for x in res_relations.values():
        x.from_field.relation = x.to_field.relation = x

    return {
        "entities": [x.to_dict() for x in sorted(
            entities.values(), key=lambda x: x.level if hasattr(x, 'level') else 0
        )],
        "relations": [x.to_dict() for x in list(res_relations.values())]
    }


def parse_markdown(s: str) -> dict[str, t.Any]:
    """
    Parse input markdown text and return a dictionary of entities and relations.
    """
    global relations_raw
    global relations
    global entities

    # Clear all comments with finditer, re.sub doesn't work idkw
    for x in reversed([*re.finditer(r"[\n]?<!--.+?-->", s, re.MULTILINE | re.DOTALL)]):
        start, end = x.span()
        s = s[:start] + s[end:]
    s = s.strip("\t\n ")

    # Get global statements: that could be either entity definition or relation
    relations_raw = []
    relations = []
    entities = {}

    for x in re.findall(
        r"""(?m)^([\w\d\ \-\,\.\"\@]+\n(?:- .*(?:\n|$))*)""", s, re.MULTILINE
    ):
        y = Entity.from_string(x)
        entities[y.name] = y

    relations += [Relation.from_string(x) for x in re.findall(
        r"[^\ \n]+\..+---.+---.+\..+", s, re.MULTILINE
    ) + relations_raw]

    return order_relations()
