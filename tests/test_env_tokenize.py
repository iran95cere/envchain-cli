"""Tests for env_tokenize module."""
import pytest
from envchain.env_tokenize import EnvTokenizer, TokenType, Token, TokenizeReport


@pytest.fixture
def tokenizer():
    return EnvTokenizer()


# --- Token tests ---

class TestToken:
    def test_repr_contains_name_and_type(self):
        tok = Token(name="FOO", value="bar", token_type=TokenType.PLAIN)
        assert "FOO" in repr(tok)
        assert "plain" in repr(tok)

    def test_to_dict_contains_required_keys(self):
        tok = Token(name="X", value="1", token_type=TokenType.NUMBER)
        d = tok.to_dict()
        assert d["name"] == "X"
        assert d["value"] == "1"
        assert d["type"] == "number"


# --- TokenizeReport tests ---

class TestTokenizeReport:
    def test_secret_count_zero_when_no_secrets(self):
        report = TokenizeReport(tokens=[
            Token("HOST", "localhost", TokenType.PLAIN),
        ])
        assert report.secret_count == 0

    def test_secret_count_correct(self):
        report = TokenizeReport(tokens=[
            Token("API_KEY", "abc", TokenType.SECRET),
            Token("TOKEN", "xyz", TokenType.SECRET),
            Token("HOST", "localhost", TokenType.PLAIN),
        ])
        assert report.secret_count == 2

    def test_by_type_groups_correctly(self):
        report = TokenizeReport(tokens=[
            Token("PORT", "8080", TokenType.NUMBER),
            Token("DEBUG", "true", TokenType.BOOLEAN),
            Token("HOST", "localhost", TokenType.PLAIN),
        ])
        assert len(report.by_type[TokenType.NUMBER]) == 1
        assert len(report.by_type[TokenType.BOOLEAN]) == 1

    def test_repr_contains_total_and_secrets(self):
        report = TokenizeReport(tokens=[
            Token("SECRET_KEY", "s", TokenType.SECRET),
        ])
        r = repr(report)
        assert "total=1" in r
        assert "secrets=1" in r


# --- EnvTokenizer classification tests ---

class TestEnvTokenizer:
    def test_url_classification(self, tokenizer):
        report = tokenizer.tokenize({"BASE_URL": "https://example.com/api"})
        assert report.tokens[0].token_type == TokenType.URL

    def test_path_classification_unix(self, tokenizer):
        report = tokenizer.tokenize({"DATA_DIR": "/var/data"})
        assert report.tokens[0].token_type == TokenType.PATH

    def test_number_classification(self, tokenizer):
        report = tokenizer.tokenize({"PORT": "8080"})
        assert report.tokens[0].token_type == TokenType.NUMBER

    def test_float_classification(self, tokenizer):
        report = tokenizer.tokenize({"RATIO": "3.14"})
        assert report.tokens[0].token_type == TokenType.NUMBER

    def test_boolean_classification(self, tokenizer):
        for val in ("true", "false", "yes", "no", "1", "0"):
            report = tokenizer.tokenize({"FLAG": val})
            assert report.tokens[0].token_type == TokenType.BOOLEAN, val

    def test_secret_classification_by_name(self, tokenizer):
        for name in ("API_KEY", "DB_PASSWORD", "AUTH_TOKEN", "SECRET"):
            report = tokenizer.tokenize({name: "somevalue"})
            assert report.tokens[0].token_type == TokenType.SECRET, name

    def test_plain_fallback(self, tokenizer):
        report = tokenizer.tokenize({"APP_NAME": "myapp"})
        assert report.tokens[0].token_type == TokenType.PLAIN

    def test_multiple_vars(self, tokenizer):
        vars_dict = {
            "PORT": "3000",
            "API_KEY": "secret123",
            "APP_NAME": "envchain",
        }
        report = tokenizer.tokenize(vars_dict)
        assert len(report.tokens) == 3
        assert report.secret_count == 1
