from __future__ import annotations

import json
from unittest import mock

import pytest

from airflow.models import Connection
from teserak.airflow.providers.teams.hooks.teams_webhook import (
    TeamsCommonHandler,
    TeamsWebhookHook,
)
from teserak.airflow.providers.teams.notifications.adaptive_card import (
    AdaptiveCard,
    Fact,
    FactSet,
    TextBlock,
    build_failure_card,
    build_success_card,
)

WEBHOOK_URL = "https://example.webhook.office.com/webhookb2/abc/IncomingWebhook/123/xyz"


class TestTeamsCommonHandler:
    """Tests for :class:`TeamsCommonHandler`."""

    def test_get_webhook_url_from_explicit_value(self):
        handler = TeamsCommonHandler()
        result = handler.get_webhook_url(None, WEBHOOK_URL)
        assert result == WEBHOOK_URL

    def test_get_webhook_url_from_conn_extra(self):
        conn = Connection(
            conn_id="teams_default",
            conn_type="teams",
            extra=json.dumps({"webhook_url": WEBHOOK_URL}),
        )
        handler = TeamsCommonHandler()
        result = handler.get_webhook_url(conn, None)
        assert result == WEBHOOK_URL

    def test_get_webhook_url_from_conn_host_fallback(self):
        conn = Connection(
            conn_id="teams_default",
            conn_type="teams",
            host=WEBHOOK_URL,
        )
        handler = TeamsCommonHandler()
        result = handler.get_webhook_url(conn, None)
        assert result == WEBHOOK_URL

    def test_get_webhook_url_explicit_overrides_conn(self):
        """Explicit webhook_url takes priority over connection extra."""
        other_url = "https://other.webhook.office.com/xyz"
        conn = Connection(
            conn_id="teams_default",
            conn_type="teams",
            extra=json.dumps({"webhook_url": WEBHOOK_URL}),
        )
        handler = TeamsCommonHandler()
        result = handler.get_webhook_url(conn, other_url)
        assert result == other_url

    def test_get_webhook_url_missing_raises(self):
        handler = TeamsCommonHandler()
        with pytest.raises(ValueError, match="Cannot get Teams webhook URL"):
            handler.get_webhook_url(None, None)

    def test_build_teams_payload_plain_message(self):
        handler = TeamsCommonHandler()
        payload_str = handler.build_teams_payload(message="Hello Teams!")
        payload = json.loads(payload_str)
        assert payload == {"text": "Hello Teams!"}

    def test_build_teams_payload_with_adaptive_card(self):
        card: AdaptiveCard = AdaptiveCard(
            type="AdaptiveCard",
            body=[
                TextBlock(type="TextBlock", text="Hello", weight="bolder")
            ],
        )
        handler = TeamsCommonHandler()
        payload_str = handler.build_teams_payload(message=None, card=card)
        payload = json.loads(payload_str)
        assert payload["type"] == "message"
        assert len(payload["attachments"]) == 1
        attachment = payload["attachments"][0]
        assert attachment["contentType"] == "application/vnd.microsoft.card.adaptive"
        assert attachment["content"]["type"] == "AdaptiveCard"

    def test_build_teams_payload_card_adds_schema_defaults(self):
        """If $schema or version are missing, they should be injected."""
        card: AdaptiveCard = AdaptiveCard(
            type="AdaptiveCard",
            body=[TextBlock(type="TextBlock", text="Test")],
        )
        handler = TeamsCommonHandler()
        payload_str = handler.build_teams_payload(message=None, card=card)
        content = json.loads(payload_str)["attachments"][0]["content"]
        assert "$schema" in content
        assert "version" in content

    def test_build_teams_payload_card_takes_precedence_over_message(self):
        card: AdaptiveCard = AdaptiveCard(
            type="AdaptiveCard",
            body=[TextBlock(type="TextBlock", text="Card body")],
        )
        handler = TeamsCommonHandler()
        payload_str = handler.build_teams_payload(message="Should be ignored", card=card)
        payload = json.loads(payload_str)
        # When card is provided, payload must use the attachment format (not "text")
        assert "attachments" in payload
        assert "text" not in payload

    def test_build_teams_payload_neither_message_nor_card_raises(self):
        handler = TeamsCommonHandler()
        with pytest.raises(ValueError, match="Either a message or a card"):
            handler.build_teams_payload(message=None, card=None)

    def test_build_teams_payload_with_factset(self):
        facts = [Fact(title="DAG", value="my_dag"), Fact(title="Status", value="OK")]
        card: AdaptiveCard = AdaptiveCard(
            type="AdaptiveCard",
            body=[FactSet(type="FactSet", facts=facts)],
        )
        handler = TeamsCommonHandler()
        payload_str = handler.build_teams_payload(message=None, card=card)
        content = json.loads(payload_str)["attachments"][0]["content"]
        fact_set = content["body"][0]
        assert fact_set["type"] == "FactSet"
        assert fact_set["facts"][0]["title"] == "DAG"


class TestTeamsWebhookHook:
    """Tests for :class:`TeamsWebhookHook`."""

    @pytest.fixture(autouse=True)
    def setup_connections(self, monkeypatch):
        """Patch get_connection to return a test connection."""
        conn = Connection(
            conn_id="teams_default",
            conn_type="teams",
            extra=json.dumps({"webhook_url": WEBHOOK_URL}),
        )
        monkeypatch.setattr(
            TeamsWebhookHook,
            "get_connection",
            lambda self, conn_id: conn,
        )

    def test_resolve_webhook_url_from_conn(self):
        hook = TeamsWebhookHook(teams_conn_id="teams_default")
        assert hook.webhook_url == WEBHOOK_URL

    def test_resolve_webhook_url_from_explicit(self):
        explicit = "https://other.webhook.office.com/xyz"
        hook = TeamsWebhookHook(webhook_url=explicit)
        assert hook.webhook_url == explicit

    def test_execute_plain_message(self):
        hook = TeamsWebhookHook(teams_conn_id="teams_default", message="Test message")
        with mock.patch.object(hook, "run") as mock_run:
            hook.execute()
            mock_run.assert_called_once()
            _, kwargs = mock_run.call_args
            payload = json.loads(kwargs.get("data") or mock_run.call_args[0][1])
            assert payload["text"] == "Test message"

    def test_execute_with_proxy(self):
        hook = TeamsWebhookHook(
            teams_conn_id="teams_default",
            message="msg",
            proxy="https://proxy.example.com:8888",
        )
        with mock.patch.object(hook, "run") as mock_run:
            hook.execute()
            _, kwargs = mock_run.call_args
            proxies = kwargs.get("extra_options", {}).get("proxies", {})
            assert proxies.get("https") == "https://proxy.example.com:8888"

    def test_execute_with_adaptive_card(self):
        card: AdaptiveCard = AdaptiveCard(
            type="AdaptiveCard",
            body=[TextBlock(type="TextBlock", text="Card test")],
        )
        hook = TeamsWebhookHook(teams_conn_id="teams_default", card=card)
        with mock.patch.object(hook, "run") as mock_run:
            hook.execute()
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            payload = json.loads(call_kwargs["data"])
            assert payload["type"] == "message"
            assert payload["attachments"][0]["contentType"] == "application/vnd.microsoft.card.adaptive"

    def test_execute_sends_json_content_type(self):
        hook = TeamsWebhookHook(teams_conn_id="teams_default", message="hi")
        with mock.patch.object(hook, "run") as mock_run:
            hook.execute()
            headers = mock_run.call_args[1]["headers"]
            assert headers["Content-Type"] == "application/json"
