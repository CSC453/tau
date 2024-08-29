import argparse
import importlib
import tomllib
import typing
import inspect  # https://docs.python.org/3/library/inspect.html
from collections import defaultdict
from typing import Optional


def basic_type(cls: typing.Any):
    orig = typing.get_origin(cls)
    v: tuple[type, str]
    if orig:
        if orig == list:
            ty = typing.get_args(cls)[0]
            v = ty, "list"
        elif orig.__name__ == "Union":
            ty = typing.get_args(cls)[0]
            v = ty, "optional"
        else:
            raise NotImplementedError(f"Unknown type constructor {orig}")
    else:
        v = cls, ""
    assert isinstance(v[0], type)
    return v


def create_types(lis: Optional[list[str]]) -> list[type]:
    if lis is None:
        return []
    return [get_module_value(x)[1] for x in lis]


def create_type_messages(d: Optional[dict[str, str]]) -> dict[type, str]:
    if d is None:
        return {}
    return {get_module_value(name)[1]: msg for name, msg in d.items()}


class Params:
    parent: Optional["Params"]
    values: dict[str, typing.Any]
    original: dict[str, typing.Any]

    prefix: str

    factory: dict[str, typing.Callable[[typing.Any], typing.Any]] = {
        "type_excludes": create_types,
        "type_messages": create_type_messages,
        "type_opaques": create_types,
        "field_excludes": lambda x: x if x is not None else [],
        "field_messages": lambda x: x if x is not None else {},
        "field_opaques": lambda x: x if x is not None else [],
        "prefix": lambda x: x if x is not None else "",
        "decl": lambda x: x if x is not None else [],
        "call": lambda x: x if x is not None else [],
        "rettype": lambda x: x if x is not None else "None",
        "initialize": lambda x: x if x is not None else {},
        "prologue": lambda x: x if x is not None else "",
        "epilogue": lambda x: x if x is not None else "",
        "inside_class": lambda x: x if x is not None else False,
        "root": lambda x: x if x else None,
        "roots": lambda x: x if x else [],
        "emit": lambda x: x if x else [],
        "include_self": lambda x: x if x is not None else True,
    }

    inherited: set[str] = {
        "type_excludes",
        "type_messages",
        "type_opaques",
        "field_excludes",
        "field_messages",
        "field_opaques",
        "prefix",
        "root",
        "inside_class",
    }

    def __init__(
        self,
        original: dict[str, typing.Any],
        parent: Optional["Params"] = None,
    ):
        self.parent = parent
        self.original = original
        self.values = {}
        o: set[str] = set(original.keys()) - set(self.factory.keys())
        if o:
            raise Exception(f"Unknown parameters {o}")
        o = set(self.field_excludes) & set(self.field_opaques)
        if o:
            raise Exception(f"Field {o} cannot be both excluded and opaque")

    def __getattr__(self, name: str) -> typing.Any:
        if name in self.values:
            return self.values[name]
        if name in self.original:
            self.values[name] = self.factory[name](self.original[name])
            return self.values[name]
        if name in self.inherited and self.parent:
            return getattr(self.parent, name)
        return self.factory[name](None)

    def is_type_excluded(self, cls: type) -> bool:
        cls, _ = basic_type(cls)
        p: Optional[Params] = self
        while p:
            for c in p.type_excludes:
                if issubclass(cls, c):
                    return True
            p = p.parent
        return False

    def is_type_opaque(self, cls: type) -> bool:
        cls, _ = basic_type(cls)
        p: Optional[Params] = self
        while p:
            for c in p.type_opaques:
                if issubclass(cls, c):
                    return True
            p = p.parent
        return False

    def get_type_message(self, cls: type) -> str:
        cls, _ = basic_type(cls)
        p: Optional[Params] = self
        while p:
            for c, msg in p.type_messages:
                if issubclass(cls, c):
                    return msg
            p = p.parent
        return ""

    def get_field_message(self, fieldname: str) -> str:
        p: Optional[Params] = self
        while p:
            if fieldname in p.field_messages:
                return p.field_messages[fieldname]
            p = p.parent
        return ""

    def is_field_excluded(self, fieldname: str) -> bool:
        p: Optional[Params] = self
        while p:
            for f in p.field_excludes:
                if fieldname == f:
                    return True
            p = p.parent
        return False

    def is_field_opaque(self, fieldname: str) -> bool:
        p: Optional[Params] = self
        while p:
            for f in p.field_opaques:
                if fieldname == f:
                    return True
            p = p.parent
        return False


Ty = typing.Union[tuple[type, tuple[type, ...]], list["Ty"]]


class Template:
    name2class: dict[str, type]
    subclasses: dict[type, list[type]]
    params: Params
    out: typing.TextIO

    selfie_call: str
    selfie_decl: str

    indent: str
    root: type
    namespace: typing.Any

    def __init__(
        self,
        root: type,
        namespace: typing.Any,
        params: Params,
        out: typing.TextIO,
    ):
        self.root = root
        self.namespace = namespace
        self.params = params
        self.selfie_call = "self." if params.inside_class else ""
        self.selfie_decl = "self, " if params.inside_class else ""
        self.indent = "    " if params.inside_class else ""
        self.name2class = self.compute_name2class()
        self.compute_subclasses()
        self.out = out

    def per_dispatcher(self, cls: type, subs: list[type], params: Params):
        i1: str = self.indent
        i2 = i1 + "    "
        i3 = i2 + "    "
        i4 = i3 + "    "
        arg_decl = "".join([f", {n}:{t}" for n, t in params.decl])
        arg_call = "".join([f", {n}" for n, _ in params.decl])

        if params.is_type_excluded(cls):
            return
        msg = params.get_type_message(cls)
        if msg:
            self.emit(i1, f"# {msg}")

        self.emit(
            i1,
            f"def {params.prefix}{cls.__name__}({self.selfie_decl}ast: asts.{cls.__name__}{arg_decl}) -> {params.rettype}:",
        )
        rv: str
        for name, ty in params.initialize.items():
            self.emit(i2, f"{name} = {ty}")
        if params.rettype != "None":
            self.emit(i2, f"retval : {params.rettype}")
            rv = "retval = "
        else:
            rv = ""
        self.emit(i2, f"match ast:")
        for sub in subs:
            self.emit(i3, f"case asts.{sub.__name__}():")
            msg = params.get_type_message(sub)
            if msg:
                self.emit(i4, f"# {msg}")
            self.emit(
                i4,
                f"{rv}{self.selfie_call}{params.prefix}{sub.__name__}(ast{arg_call})",
            )
        self.emit(i3, "case _:")
        self.emit(i4, f"raise NotImplementedError(f'Unknown type {{ast}}')")
        if params.rettype != "None":
            self.emit(i2, f"return retval")

    def per_class(self, cls: type, params: Params):
        n: str = cls.__name__
        indent1: str = self.indent
        indent2 = indent1 + "    "
        arg_decl = "".join([f", {n}:{t}" for n, t in params.decl])

        msg = params.get_type_message(cls)
        if msg:
            self.emit(indent1, f"# {msg}")

        self.emit(
            indent1,
            f"def {params.prefix}{n}({self.selfie_decl}ast: asts.{n}{arg_decl}) -> {params.rettype}:",
        )
        fieldname: str
        fieldtype: type
        code: list[str] = []
        comments: list[str] = []
        for fieldname, fieldtype in typing.get_type_hints(cls).items():
            s: str = self.per_field(indent2, fieldname, fieldtype, params)
            if not s:
                continue
            if "#" in s:
                comments.append(s)
            else:
                code.append(s)
        c: str
        for c in comments:
            self.emit("", c)
        for name, ty in params.initialize.items():
            self.emit(indent2, f"{name} = {ty}")
        if params.rettype != "None":
            self.emit(indent2, f"retval : {params.rettype}")
        if params.prologue:
            self.emit(indent2, params.prologue)
        for c in code:
            self.emit("", c)
        if params.epilogue:
            self.emit(indent2, params.epilogue)
        if params.rettype != "None":
            self.emit(indent2, f"return retval")
        if (
            not code
            and not params.initialize
            and not params.prologue
            and not params.epilogue
            and params.rettype == "None"
        ):
            self.emit(indent2, f"pass")

    def per_field(
        self, indent: str, fieldname: str, fieldtype: type, params: Params
    ) -> str:
        if fieldname.startswith("__"):
            return ""

        if params.is_field_excluded(fieldname) or params.is_type_excluded(fieldtype):
            return ""

        msg = params.get_field_message(fieldname) + params.get_type_message(fieldtype)
        suffix: str = f"  # {msg}" if msg else ""

        ty: type
        orig: str
        ty, orig = basic_type(fieldtype)

        if params.is_field_opaque(fieldname) or params.is_type_opaque(fieldtype):
            dec: str
            if orig == "list":
                dec = f"ast.{fieldname} : list[{ty.__name__}]"
            elif orig == "optional":
                dec = f"ast.{fieldname} : Optional[{ty.__name__}]"
            else:
                dec = f"ast.{fieldname} : {ty.__name__}"
            return f"{indent}# {dec} {msg}"

        arg_call = "".join([f", {n}" for n, _ in params.call])
        retval: str = ""

        assert issubclass(
            ty, self.root
        ), f"[{fieldname}] {ty} is not a subclass of {self.root}"

        if orig:
            if orig == "list":
                singular = fieldname[:-1]
                retval = f"for {singular} in ast.{fieldname}: {self.selfie_call}{params.prefix}{ty.__name__}({singular}{arg_call})"
                if "$FIELD$" in arg_call:
                    retval = f"for index, {singular} in enumerate(ast.{fieldname}): {self.selfie_call}{params.prefix}{ty.__name__}({singular}{arg_call})"
                    retval = retval.replace("$FIELD$", f'f"{fieldname}[{{index}}]"')
            elif orig == "optional":
                retval = f"if ast.{fieldname}:{self.selfie_call}{params.prefix}{ty.__name__}(ast.{fieldname}{arg_call})"
                retval = retval.replace("$FIELD$", f'"{fieldname}"')
            else:
                raise NotImplementedError(f"Unknown type constructor {orig}")
        else:
            retval = f"{self.selfie_call}{params.prefix}{fieldtype.__name__}(ast.{fieldname}{arg_call}){suffix}"
            retval = retval.replace("$FIELD$", f'"{fieldname}"')
        retval = f"{indent}{retval}"
        return retval

    def emit(self, indent: str, s: str) -> None:
        self.out.write(f"{indent}{s}\n")

    # Ty = typing.Union[
    #     tuple[type, tuple[type, ...]],
    #     list["Ty"]
    #     ]

    def compute_subclasses0(self, tree: Ty):
        if isinstance(tree, list):
            v: Ty
            for v in tree:
                self.compute_subclasses0(v)
            return
        cls: type
        supercls: type
        others: list[type]
        match tree:
            case (cls, ()):
                pass
            case (cls, (supercls, *others)):
                if issubclass(supercls, self.root):
                    assert len(others) == 0
                    self.subclasses[supercls].append(cls)
            case _:
                raise NotImplementedError(f"Unknown type {tree}")

    def compute_subclasses(self):
        self.subclasses = defaultdict(list)
        tree = inspect.getclasstree(list(self.name2class.values()), unique=True)
        self.compute_subclasses0(tree)

    def compute_name2class(self):
        name2class = {
            n: c
            for n, c in inspect.getmembers(self.namespace)
            if isinstance(c, type) and issubclass(c, self.root)
        }
        return name2class

    def transitive(self, cls: type, params: Params, include_self: bool):
        if params.is_type_excluded(cls):
            return
        if cls in self.subclasses:
            subclasses = self.subclasses[cls]
            subclasses.sort(key=lambda c: (c in self.subclasses, c.__name__))
            if include_self:
                self.per_dispatcher(cls, subclasses, params)
            for sub in subclasses:
                self.transitive(sub, params, True)
        else:
            if include_self:
                self.per_class(cls, params)


def main():
    args = get_args()
    spec = args.spec
    with open(spec, "rb") as f:
        d: dict[str, typing.Any] = tomllib.load(f)  # type: ignore
        outname = args.output
        with open(outname, "w") as out:
            process(d, out)  # type: ignore


def get_module_value(s: str):
    vs = s.split(".")
    mod = importlib.import_module(".".join(vs[:-1]))
    root = getattr(mod, vs[-1])
    return mod, root


def process(d: dict[str, typing.Any], out: typing.TextIO):
    mod, root = get_module_value(d["root"])
    parent = Params(d)
    t = Template(root, mod, parent, out)
    out.write("# pyright: reportUnboundVariable=none, reportUnusedFunction=none\n")
    if parent.prologue:
        out.write(parent.prologue)
        out.write("\n")

    for e in parent.emit:
        params = Params(e, parent)
        for r in params.roots:
            mod, root = get_module_value(r)
            t.transitive(root, params, params.include_self)

    if parent.epilogue:
        out.write(parent.epilogue)
        out.write("\n")


def mk_type_list(lis: list[str]) -> set[type]:
    return set(get_module_value(x)[1] for x in lis)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, required=True, help="Output file")
    parser.add_argument("--spec", type=str, required=True, help="TOML file to process")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
