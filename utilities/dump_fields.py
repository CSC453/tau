from typing import Any, Callable
from tau import asts

excludes: set[str] = {
    "span",
    "offset",
    "size",
    "register_pool",
    "register",
}


def all_slots(obj: asts.AST) -> set[str]:
    slots: set[str] = set()
    cls: type
    for cls in obj.__class__.__mro__:
        slots.update(getattr(cls, "__slots__", []))
    return slots


def mk_fn() -> tuple[Callable[[asts.AST], None], list[dict[str, str]]]:
    found: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()

    def log(cls: str, slot: str, vtype: str, kind: str) -> None:
        tup = (cls, slot, vtype, kind)
        if tup not in seen:
            seen.add(tup)
            d: dict[str, str] = {"class": cls}
            if slot:
                d["field"] = slot
            if vtype:
                d["field_type"] = vtype
            if kind:
                d["token"] = kind
            found.append(d)

    def dump(ast: asts.AST) -> None:
        slots = all_slots(ast)
        field: bool = False
        for slot in slots:
            if slot in excludes:
                continue
            field = True
            cls = ast.__class__.__name__
            assert cls is not None, f"{ast.__class__.__name__} is None"
            v: Any | None = getattr(ast, slot) if hasattr(ast, slot) else None
            vtype: Any | str = v.__class__.__name__
            assert (
                vtype is not None
            ), f"{ast.__class__.__name__}:{slot} is None"
            if isinstance(v, list):
                if len(v) == 0: # type: ignore
                    field_type = "<empty>"
                    log(cls, slot, field_type, "")
                else:
                    for i in v: # type: ignore
                        assert isinstance(i.__class__, type) # type: ignore
                        field_type = i.__class__.__name__ # type: ignore
                        log(cls, slot, field_type, "")
                continue
            kind = getattr(v, "kind", "")
            log(cls, slot, vtype, kind)
        if not field:
            cls = ast.__class__.__name__
            assert cls is not None, f"{ast.__class__.__name__} is None"
            log(cls, "", "", "")

    return dump, found
