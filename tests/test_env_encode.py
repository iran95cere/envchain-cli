"""Tests for envchain.env_encode."""
import base64
import urllib.parse

import pytest

from envchain.env_encode import EncodeFormat, EncodeResult, EncodeReport, EnvEncoder


@pytest.fixture
def encoder():
    return EnvEncoder()


@pytest.fixture
def sample_vars():
    return {"DB_URL": "postgres://localhost/db", "TOKEN": "abc 123", "PORT": "5432"}


class TestEncodeResult:
    def test_repr_encoded(self):
        r = EncodeResult("K", "v", "dg==", EncodeFormat.BASE64, changed=True)
        assert "encoded" in repr(r)
        assert "K" in repr(r)

    def test_repr_unchanged(self):
        r = EncodeResult("K", "v", "v", EncodeFormat.URL, changed=False)
        assert "unchanged" in repr(r)


class TestEncodeReport:
    def test_encoded_count_zero_when_no_changes(self):
        report = EncodeReport(results=[])
        assert report.encoded_count == 0

    def test_has_changes_false_when_empty(self):
        assert not EncodeReport().has_changes

    def test_has_changes_true_when_changed(self):
        r = EncodeResult("A", "x", "eA==", EncodeFormat.BASE64, changed=True)
        report = EncodeReport(results=[r])
        assert report.has_changes

    def test_to_dict_contains_required_keys(self):
        report = EncodeReport(results=[])
        d = report.to_dict()
        assert "encoded_count" in d
        assert "total" in d
        assert "results" in d


class TestEnvEncoder:
    def test_encode_base64(self, encoder, sample_vars):
        report = encoder.encode(sample_vars, EncodeFormat.BASE64)
        for result in report.results:
            expected = base64.b64encode(sample_vars[result.name].encode()).decode()
            assert result.encoded == expected

    def test_decode_base64_roundtrip(self, encoder, sample_vars):
        encoded_vars = {
            k: base64.b64encode(v.encode()).decode() for k, v in sample_vars.items()
        }
        report = encoder.decode(encoded_vars, EncodeFormat.BASE64)
        for result in report.results:
            assert result.encoded == sample_vars[result.name]

    def test_encode_url(self, encoder):
        vars_ = {"PATH": "/some/path with spaces"}
        report = encoder.encode(vars_, EncodeFormat.URL)
        assert report.results[0].encoded == "%2Fsome%2Fpath%20with%20spaces"

    def test_decode_url(self, encoder):
        vars_ = {"PATH": "%2Fsome%2Fpath%20with%20spaces"}
        report = encoder.decode(vars_, EncodeFormat.URL)
        assert report.results[0].encoded == "/some/path with spaces"

    def test_encode_hex(self, encoder):
        vars_ = {"KEY": "hi"}
        report = encoder.encode(vars_, EncodeFormat.HEX)
        assert report.results[0].encoded == "6869"

    def test_decode_hex(self, encoder):
        vars_ = {"KEY": "6869"}
        report = encoder.decode(vars_, EncodeFormat.HEX)
        assert report.results[0].encoded == "hi"

    def test_changed_false_when_already_encoded(self, encoder):
        val = base64.b64encode(b"hello").decode()
        report = encoder.encode({"X": val}, EncodeFormat.BASE64)
        # re-encoding a b64 string changes it
        assert report.results[0].changed

    def test_decode_invalid_hex_returns_original(self, encoder):
        vars_ = {"K": "not-hex!"}
        report = encoder.decode(vars_, EncodeFormat.HEX)
        assert report.results[0].encoded == "not-hex!"

    def test_formats_list_non_empty(self):
        assert len(EnvEncoder.FORMATS) >= 3
