"""Integration tests for encode/decode roundtrip via storage."""
import tempfile
from pathlib import Path

import pytest

from envchain.env_encode import EncodeFormat, EnvEncoder
from envchain.models import Profile
from envchain.storage import EnvStorage


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def storage(tmp_dir):
    return EnvStorage(storage_dir=str(tmp_dir))


def _save_profile(storage, name: str, vars_: dict) -> Profile:
    p = Profile(name=name)
    p.variables = dict(vars_)
    storage.save_profile(p)
    return p


class TestEnvEncoderIntegration:
    def test_base64_roundtrip_via_storage(self, storage):
        original = {"DB_PASS": "s3cr3t!", "HOST": "localhost"}
        _save_profile(storage, "prod", original)

        encoder = EnvEncoder()
        profile = storage.load_profile("prod")
        encode_report = encoder.encode(dict(profile.variables), EncodeFormat.BASE64)
        for r in encode_report.results:
            profile.variables[r.name] = r.encoded
        storage.save_profile(profile)

        reloaded = storage.load_profile("prod")
        decode_report = encoder.decode(dict(reloaded.variables), EncodeFormat.BASE64)
        decoded = {r.name: r.encoded for r in decode_report.results}
        assert decoded == original

    def test_hex_roundtrip_via_storage(self, storage):
        original = {"API_KEY": "abc123", "PORT": "8080"}
        _save_profile(storage, "staging", original)

        encoder = EnvEncoder()
        profile = storage.load_profile("staging")
        enc_report = encoder.encode(dict(profile.variables), EncodeFormat.HEX)
        for r in enc_report.results:
            profile.variables[r.name] = r.encoded
        storage.save_profile(profile)

        reloaded = storage.load_profile("staging")
        dec_report = encoder.decode(dict(reloaded.variables), EncodeFormat.HEX)
        decoded = {r.name: r.encoded for r in dec_report.results}
        assert decoded == original

    def test_url_encode_changes_special_chars(self, storage):
        original = {"REDIRECT": "https://example.com/path?a=1&b=2"}
        _save_profile(storage, "web", original)

        encoder = EnvEncoder()
        profile = storage.load_profile("web")
        report = encoder.encode(dict(profile.variables), EncodeFormat.URL)
        assert report.results[0].changed
        assert "%" in report.results[0].encoded
