"""Tokenize environment variable values into typed tokens."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class TokenType(str, Enum):
    URL = "url"
    PATH = "path"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SECRET = "secret"
    PLAIN = "plain"


_URL_RE = re.compile(r"^https?://\S+", re.IGNORECASE)
_PATH_RE = re.compile(r"^[/~]\S*|^[A-Za-z]:\\\S*")
_NUMBER_RE = re.compile(r"^-?\d+(\.\d+)?$")
_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0"}
_SECRET_HINTS = re.compile(
    r"(password|secret|token|key|api_key|auth|credential)", re.IGNORECASE
)


@dataclass
class Token:
    name: str
    value: str
    token_type: TokenType

    def __repr__(self) -> str:
        return f"Token(name={self.name!r}, type={self.token_type.value})"

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value, "type": self.token_type.value}


@dataclass
class TokenizeReport:
    tokens: List[Token] = field(default_factory=list)

    @property
    def by_type(self) -> Dict[TokenType, List[Token]]:
        result: Dict[TokenType, List[Token]] = {}
        for tok in self.tokens:
            result.setdefault(tok.token_type, []).append(tok)
        return result

    @property
    def secret_count(self) -> int:
        return sum(1 for t in self.tokens if t.token_type == TokenType.SECRET)

    def __repr__(self) -> str:
        return f"TokenizeReport(total={len(self.tokens)}, secrets={self.secret_count})"


class EnvTokenizer:
    """Classify environment variable name/value pairs into typed tokens."""

    def tokenize(self, vars_dict: Dict[str, str]) -> TokenizeReport:
        tokens = [Token(name=k, value=v, token_type=self._classify(k, v))
                  for k, v in vars_dict.items()]
        return TokenizeReport(tokens=tokens)

    def _classify(self, name: str, value: str) -> TokenType:
        if _SECRET_HINTS.search(name):
            return TokenType.SECRET
        if _URL_RE.match(value):
            return TokenType.URL
        if _PATH_RE.match(value):
            return TokenType.PATH
        if _NUMBER_RE.match(value):
            return TokenType.NUMBER
        if value.lower() in _BOOL_VALUES:
            return TokenType.BOOLEAN
        return TokenType.PLAIN
