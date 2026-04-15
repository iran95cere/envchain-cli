"""Tests for envchain.env_split."""
from __future__ import annotations

import pytest

from envchain.env_split import EnvSplitter, SplitReport, SplitResult


@pytest.fixture()
def splitter() -> EnvSplitter:
    return EnvSplitter()


@pytest.fixture()
def sample_vars() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "APP_NAME": "myapp",
        "UNTAGGED": "value",
    }


class TestSplitResult:
    def test_var_count(self):
        r = SplitResult(prefix="DB_", vars={"DB_HOST": "localhost"})
        assert r.var_count == 1

    def test_var_count_empty(self):
        r = SplitResult(prefix="DB_")
        assert r.var_count == 0


class TestSplitReport:
    def test_group_count(self):
        r = SplitReport(
            results=[SplitResult(prefix="A_"), SplitResult(prefix="B_")]
        )
        assert r.group_count == 2

    def test_unmatched_count(self):
        r = SplitReport(unmatched={"X": "1", "Y": "2"})
        assert r.unmatched_count == 2

    def test_has_unmatched_false_when_empty(self):
        r = SplitReport()
        assert not r.has_unmatched

    def test_has_unmatched_true_when_present(self):
        r = SplitReport(unmatched={"X": "1"})
        assert r.has_unmatched


class TestEnvSplitter:
    def test_split_groups_by_prefix(self, splitter, sample_vars):
        report = splitter.split(sample_vars, ["DB_", "AWS_"])
        prefixes = {r.prefix for r in report.results}
        assert "DB_" in prefixes
        assert "AWS_" in prefixes

    def test_split_correct_vars_in_group(self, splitter, sample_vars):
        report = splitter.split(sample_vars, ["DB_"])
        db = next(r for r in report.results if r.prefix == "DB_")
        assert "DB_HOST" in db.vars
        assert "DB_PORT" in db.vars

    def test_unmatched_vars_captured(self, splitter, sample_vars):
        report = splitter.split(sample_vars, ["DB_", "AWS_"])
        assert "APP_NAME" in report.unmatched
        assert "UNTAGGED" in report.unmatched

    def test_strip_prefix_removes_prefix_from_keys(self, splitter, sample_vars):
        report = splitter.split(sample_vars, ["DB_"], strip_prefix=True)
        db = next(r for r in report.results if r.prefix == "DB_")
        assert "HOST" in db.vars
        assert "PORT" in db.vars
        assert "DB_HOST" not in db.vars

    def test_no_matching_prefix_returns_empty_results(self, splitter):
        report = splitter.split({"FOO": "bar"}, ["DB_"])
        assert report.group_count == 0
        assert "FOO" in report.unmatched

    def test_first_matching_prefix_wins(self, splitter):
        vars_ = {"DB_HOST": "localhost"}
        report = splitter.split(vars_, ["DB_", "DB_H"])
        db = next(r for r in report.results if r.prefix == "DB_")
        assert "DB_HOST" in db.vars
        db_h_results = [r for r in report.results if r.prefix == "DB_H"]
        assert not db_h_results

    def test_empty_vars_returns_empty_report(self, splitter):
        report = splitter.split({}, ["DB_", "AWS_"])
        assert report.group_count == 0
        assert not report.has_unmatched

    def test_empty_prefixes_all_unmatched(self, splitter, sample_vars):
        report = splitter.split(sample_vars, [])
        assert report.group_count == 0
        assert report.unmatched_count == len(sample_vars)
