from typing import List, Optional
from .tokens import Span


class SemanticType:
    __slots__: list[str] = []

    def size(self) -> int:
        assert False, f"{type(self)}.size() not implemented"

    def shallow_representation(self) -> str:
        return f"{self.__class__.__name__}()"


class Phony_Type(SemanticType):
    def __repr__(self) -> str:
        return "Phony_Type()"


class VoidType(SemanticType):
    __slots__: list[str] = []

    def size(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "VoidType()"


class IntType(SemanticType):
    __slots__: list[str] = []

    def size(self) -> int:
        return 1

    def __repr__(self) -> str:
        return "IntType()"


class BoolType(SemanticType):
    __slots__: list[str] = []

    def size(self) -> int:
        return 1

    def __repr__(self) -> str:
        return "BoolType()"


class ArrayType(SemanticType):
    element_type: SemanticType
    count: int
    __slots__: list[str] = ["element_type", "count"]

    def __init__(self, element_type: SemanticType, count: int):
        self.element_type = element_type
        self.count = count

    def size(self) -> int:
        return self.element_type.size() * self.count

    def shallow_representation(self) -> str:
        return f"{self.__class__.__name__}(element_type={self.element_type.shallow_representation()})"

    def __repr__(self) -> str:
        return f"ArrayType(count={self.count}, element_type={self.element_type})"


class FuncType(SemanticType):
    params: list[SemanticType]
    ret: SemanticType
    param_size: int
    frame_size: int
    __slots__ = ["params", "ret", "param_size", "frame_size"]

    def __init__(self, params: List[SemanticType], ret: SemanticType):
        self.params: list[SemanticType] = params
        self.ret: SemanticType = ret
        self.param_size: int = 0
        self.frame_size: int = 0

    def __repr__(self) -> str:
        return f"Functype(params={self.params}, ret={self.ret})"


class Symbol:
    name: str
    scope: "Scope"
    _semantic_type: SemanticType
    offset: int

    __slots__: list[str] = ["name", "scope", "_semantic_type", "offset"]

    def __init__(self, name: str, scope: "Scope") -> None:
        self.name: str = name
        self.scope: Scope = scope
        self._semantic_type: SemanticType = Phony_Type()
        self.offset = -999999

    def set_type(self, t: SemanticType) -> None:
        self._semantic_type = t

    def get_type(self) -> SemanticType:
        return self._semantic_type

    def __repr__(self) -> str:
        return f"Symbol({self.name}, {self._semantic_type})"

    def shallow_representation(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, offset={self.offset}, type={self._semantic_type.shallow_representation()}, scope={self.scope.shallow_representation()})"


class Phony_Symbol(Symbol):
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "Phony_Symbol()"


class Scope:
    symtab: dict[str, Symbol]
    parent: Optional["Scope"]
    span: Span
    __slots__: list[str] = ["symtab", "parent", "span"]

    def lookup(self, name: str) -> Symbol | None:
        if name in self.symtab:
            return self.symtab[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def depth(self) -> int:
        if self.parent:
            return self.parent.depth() + 1
        return 0

    def shallow_representation(self) -> str:
        parent = self.parent.shallow_representation() if self.parent else ""
        keys = sorted(list(self.symtab.keys()))
        return f"{self.__class__.__name__}(values={keys}, span={self.span}, parent={parent})"

    def __repr__(self) -> str:
        return self.shallow_representation()


class Phony_Scope(Scope):
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "Phony_Scope()"


# holds parameters
class FuncScope(Scope):
    __slots__: list[str] = []

    def __init__(self, parent: Scope, span: Span) -> None:
        self.symtab = {}
        self.parent = parent
        self.span = span


# holds symbols in compound statement
class LocalScope(Scope):
    __slots__: list[str] = []

    def __init__(self, parent: Scope, span: Span) -> None:
        self.parent = parent
        self.span: Span = span
        self.symtab: dict[str, Symbol] = {}


# holds global symbols (i.e., function declarations)
class GlobalScope(Scope):
    __slots__: list[str] = []

    def __init__(self, span: Span) -> None:
        self.span: Span = span
        self.symtab: dict[str, Symbol] = {}
        self.parent = None
