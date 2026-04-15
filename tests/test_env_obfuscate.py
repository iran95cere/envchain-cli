"""Tests for EnvObfuscator and related data-classes."""
import base64

import pytest

from envchain.env_obfuscate import EnvObfuscator, ObfuscateReport, ObfuscateResult


@pytest.fixture()
def obfuscator() -> EnvObfuscator:
    return EnvObfuscator()


@pytest.fixture()
def sample_vars() -> dict:
    return {"DB_PASS": "secret", "API_KEY": "abc123"}


class TestObfuscateResult:
    def test_changed_true_when_values_differ(self):
        r = ObfuscateResult("X", "plain", "obf:xxx", changed=True)
        assert r.changed is True

    def test_changed_false_when_values_same(self):
        r = ObfuscateResult("X", "obf:xxx", "obf:xxx", changed=False)
        assert r.changed is False


class TestObfuscateReport:
    def test_obfuscated_count_zero_when_empty(self):
        report = ObfuscateReport()
        assert report.obfuscated_count == 0

    def test_has_changes_false_when_empty(self):
        report = ObfuscateReport()
        assert report.has_changes is False

    def test_obfuscated_count_counts_changed(self):
        results = [
            ObfuscateResult("A", "v", "obf:v", changed=True),
            ObfuscateResult("B", "obf:v", "obf:v", changed=False),
        ]
        report = ObfuscateReport(results=results)
        assert report.obfuscated_count == 1

    def test_has_changes_true_when_any_changed(self):
        results = [ObfuscateResult("A", "v", "obf:v", changed=True)]
        report = ObfuscateReport(results=results)
        assert report.has_changes is True


class TestEnvObfuscator:
    def test_obfuscate_encodes_plain_values(self, obfuscator, sample_vars):
        report = obfuscator.obfuscate(sample_vars)
        for r in report.results:
            assert r.obfuscated.startswith(EnvObfuscator.PREFIX)
            assert r.changed is True

    def test_obfuscate_skips_already_obfuscated(self, obfuscator):
        already = {"X": "obf:" + base64.b64encode(b"val").decode()}
        report = obfuscator.obfuscate(already)
        assert report.obfuscated_count == 0
        assert report.results[0].changed is False

    def test_deobfuscate_restores_original(self, obfuscator, sample_vars):
        obf_report = obfuscator.obfuscate(sample_vars)
        obf_dict = obfuscator.to_flat_dict(obf_report)
        deobf_report = obfuscator.deobfuscate(obf_dict)
        restored = obfuscator.to_flat_dict(deobf_report)
        assert restored == sample_vars

    def test_deobfuscate_skips_plain_values(self, obfuscator):
        report = obfuscator.deobfuscate({"KEY": "plaintext"})
        assert report.obfuscated_count == 0
        assert report.results[0].changed is False

    def test_to_flat_dict_returns_correct_mapping(self, obfuscator, sample_vars):
        report = obfuscator.obfuscate(sample_vars)
        flat = obfuscator.to_flat_dict(report)
        assert set(flat.keys()) == set(sample_vars.keys())
        for v in flat.values():
            assert v.startswith(EnvObfuscator.PREFIX)

    def test_roundtrip_preserves_special_characters(self, obfuscator):
        vars_ = {"SPECIAL": "p@$$w0rd!\nwith\nnewlines"}
        flat = obfuscator.to_flat_dict(obfuscator.obfuscate(vars_))
        restored = obfuscator.to_flat_dict(obfuscator.deobfuscate(flat))
        assert restored == vars_
