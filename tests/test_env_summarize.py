import pytest
from envchain.env_summarize import SummaryEntry, SummaryReport, EnvSummarizer


@pytest.fixture
def summarizer():
    return EnvSummarizer()


@pytest.fixture
def sample_vars():
    return {"DATABASE_URL": "postgres://localhost", "SECRET_KEY": "abc", "EMPTY_VAR": ""}


class TestSummaryEntry:
    def test_to_dict_contains_required_keys(self):
        entry = SummaryEntry(
            profile="dev", total_vars=3, empty_vars=1,
            longest_key="DATABASE_URL", longest_value_len=18
        )
        d = entry.to_dict()
        assert "profile" in d
        assert "total_vars" in d
        assert "empty_vars" in d
        assert "longest_key" in d
        assert "longest_value_len" in d

    def test_from_dict_roundtrip(self):
        entry = SummaryEntry(
            profile="prod", total_vars=5, empty_vars=0,
            longest_key="LONG_KEY_NAME", longest_value_len=42
        )
        restored = SummaryEntry.from_dict(entry.to_dict())
        assert restored.profile == entry.profile
        assert restored.total_vars == entry.total_vars
        assert restored.empty_vars == entry.empty_vars
        assert restored.longest_key == entry.longest_key
        assert restored.longest_value_len == entry.longest_value_len

    def test_from_dict_missing_optional_fields_use_defaults(self):
        entry = SummaryEntry.from_dict({"profile": "x", "total_vars": 2})
        assert entry.empty_vars == 0
        assert entry.longest_key == ""
        assert entry.longest_value_len == 0

    def test_repr_contains_profile_and_total(self):
        entry = SummaryEntry("staging", 7, 2, "KEY", 10)
        r = repr(entry)
        assert "staging" in r
        assert "7" in r


class TestEnvSummarizer:
    def test_summarize_counts_total_vars(self, summarizer, sample_vars):
        entry = summarizer.summarize("dev", sample_vars)
        assert entry.total_vars == 3

    def test_summarize_counts_empty_vars(self, summarizer, sample_vars):
        entry = summarizer.summarize("dev", sample_vars)
        assert entry.empty_vars == 1

    def test_summarize_finds_longest_key(self, summarizer, sample_vars):
        entry = summarizer.summarize("dev", sample_vars)
        assert entry.longest_key == "DATABASE_URL"

    def test_summarize_finds_longest_value_len(self, summarizer, sample_vars):
        entry = summarizer.summarize("dev", sample_vars)
        assert entry.longest_value_len == len("postgres://localhost")

    def test_summarize_empty_profile(self, summarizer):
        entry = summarizer.summarize("empty", {})
        assert entry.total_vars == 0
        assert entry.empty_vars == 0
        assert entry.longest_key == ""
        assert entry.longest_value_len == 0

    def test_summarize_all_returns_report(self, summarizer, sample_vars):
        report = summarizer.summarize_all({"dev": sample_vars, "prod": {"KEY": "val"}})
        assert isinstance(report, SummaryReport)
        assert report.profile_count == 2
        assert report.total_vars == 4

    def test_summarize_all_empty_input(self, summarizer):
        report = summarizer.summarize_all({})
        assert report.profile_count == 0
        assert report.total_vars == 0
