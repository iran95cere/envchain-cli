"""Environment variable encoding/decoding utilities."""
from __future__ import annotations

import base64
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class EncodeFormat(str, Enum):
    BASE64 = "base64"
    URL = "url"
    HEX = "hex"


@dataclass
class EncodeResult:
    name: str
    original: str
    encoded: str
    fmt: EncodeFormat
    changed: bool

    def __repr__(self) -> str:
        status = "encoded" if self.changed else "unchanged"
        return f"<EncodeResult name={self.name!r} fmt={self.fmt.value} {status}>"


@dataclass
class EncodeReport:
    results: List[EncodeResult] = field(default_factory=list)

    @property
    def encoded_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.encoded_count > 0

    def to_dict(self) -> Dict:
        return {
            "encoded_count": self.encoded_count,
            "total": len(self.results),
            "results": [
                {"name": r.name, "fmt": r.fmt.value, "changed": r.changed}
                for r in self.results
            ],
        }


class EnvEncoder:
    """Encode or decode environment variable values."""

    FORMATS = [f.value for f in EncodeFormat]

    def encode(self, vars_: Dict[str, str], fmt: EncodeFormat) -> EncodeReport:
        results = []
        for name, value in vars_.items():
            encoded = self._encode_value(value, fmt)
            results.append(
                EncodeResult(
                    name=name,
                    original=value,
                    encoded=encoded,
                    fmt=fmt,
                    changed=(encoded != value),
                )
            )
        return EncodeReport(results=results)

    def decode(self, vars_: Dict[str, str], fmt: EncodeFormat) -> EncodeReport:
        results = []
        for name, value in vars_.items():
            decoded = self._decode_value(value, fmt)
            results.append(
                EncodeResult(
                    name=name,
                    original=value,
                    encoded=decoded,
                    fmt=fmt,
                    changed=(decoded != value),
                )
            )
        return EncodeReport(results=results)

    def _encode_value(self, value: str, fmt: EncodeFormat) -> str:
        if fmt == EncodeFormat.BASE64:
            return base64.b64encode(value.encode()).decode()
        if fmt == EncodeFormat.URL:
            return urllib.parse.quote(value, safe="")
        if fmt == EncodeFormat.HEX:
            return value.encode().hex()
        return value

    def _decode_value(self, value: str, fmt: EncodeFormat) -> str:
        try:
            if fmt == EncodeFormat.BASE64:
                return base64.b64decode(value.encode()).decode()
            if fmt == EncodeFormat.URL:
                return urllib.parse.unquote(value)
            if fmt == EncodeFormat.HEX:
                return bytes.fromhex(value).decode()
        except Exception:
            return value
        return value
