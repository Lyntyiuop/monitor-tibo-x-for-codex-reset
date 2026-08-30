from src.config import Account


def test_account_feed_url_uses_default_rsshub_base_url(monkeypatch):
    monkeypatch.delenv("RSSHUB_BASE_URL", raising=False)
    account = Account("Tibo", "thsottiaux", "{rsshub_base_url}/twitter/user/{handle}")
    assert account.feed_url == "https://rsshub.app/twitter/user/thsottiaux"


def test_account_feed_url_uses_configured_rsshub_base_url(monkeypatch):
    monkeypatch.setenv("RSSHUB_BASE_URL", "https://rsshub.example.com/")
    account = Account("Tibo", "thsottiaux", "{rsshub_base_url}/twitter/user/{handle}")
    assert account.feed_url == "https://rsshub.example.com/twitter/user/thsottiaux"
