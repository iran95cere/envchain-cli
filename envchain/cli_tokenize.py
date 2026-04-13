"""CLI command for tokenizing environment variable values."""
from __future__ import annotations

import sys
from typing import Optional

from envchain.env_tokenize import EnvTokenizer, TokenType
from envchain.storage import EnvStorage


class TokenizeCommand:
    def __init__(self, storage: EnvStorage) -> None:
        self._storage = storage
        self._tokenizer = EnvTokenizer()

    def run(self, profile_name: str, password: str,
            filter_type: Optional[str] = None) -> None:
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._tokenizer.tokenize(profile.vars)

        if filter_type:
            try:
                wanted = TokenType(filter_type.lower())
            except ValueError:
                valid = ", ".join(t.value for t in TokenType)
                print(f"Unknown type '{filter_type}'. Valid: {valid}", file=sys.stderr)
                sys.exit(1)
            tokens = report.by_type.get(wanted, [])
        else:
            tokens = report.tokens

        if not tokens:
            print("No variables match.")
            return

        col = 28
        print(f"{'NAME':<{col}} TYPE")
        print("-" * (col + 12))
        for tok in tokens:
            print(f"{tok.name:<{col}} {tok.token_type.value}")

    def summary(self, profile_name: str, password: str) -> None:
        profile = self._storage.load_profile(profile_name, password)
        if profile is None:
            print(f"Profile '{profile_name}' not found.", file=sys.stderr)
            sys.exit(1)

        report = self._tokenizer.tokenize(profile.vars)
        print(repr(report))
        for ttype, tokens in report.by_type.items():
            print(f"  {ttype.value}: {len(tokens)}")
