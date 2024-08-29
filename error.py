from dataclasses import dataclass

from .tokens import Span


@dataclass(slots=True)
class CompileError(Exception):
    msg: str
    span: Span


@dataclass(slots=True)
class TypeError(CompileError):
    pass


@dataclass(slots=True)
class ScanError(CompileError):
    pass


@dataclass(slots=True)
class NameError(CompileError):
    pass
