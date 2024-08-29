import typing


class Coord(typing.NamedTuple):
    line: int
    col: int


class Span(typing.NamedTuple):
    start: Coord
    end: Coord


class Token(typing.NamedTuple):
    kind: str
    value: str
    span: Span


punctuation: list[str] = [
    ":",
    ",",
    "!=",
    "&",
    "*",
    "/",
    "%",
    "<=",
    "<",
    ">=",
    ">",
    "==",
    "|",
    "=",
    "+",
    "-",
    "[",
    "]",
    "{",
    "}",
    "(",
    ")",
]

keywords: list[str] = [
    "and",
    "bool",
    "call",
    "else",
    "false",
    "func",
    "if",
    "int",
    "length",
    "not",
    "or",
    "print",
    "return",
    "true",
    "var",
    "void",
    "while",
]

kinds: list[str] = ["ID", "INT", "EOF"] + punctuation + keywords
