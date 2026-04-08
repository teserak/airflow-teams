from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from airflow.providers.http.hooks.http import HttpHook

if TYPE_CHECKING:
    from airflow.models import Connection
    from teserak.airflow.providers.teams.notifications.adaptive_card import AdaptiveCard

_ADAPTIVE_CARD_SCHEMA = "http://adaptivecards.io/schemas/adaptive-card.json"
_ADAPTIVE_CARD_VERSION = "1.5"


class TeamsCommonHandler:
    """Contains the common (sync/async-agnostic) functionality for Teams webhooks."""

    def get_webhook_url(self, conn: Connection | None, webhook_url: str | None) -> str:
        """
        Return the webhook URL from an explicit value or a stored connection.

        :param conn: Airflow Teams connection.
        :param webhook_url: Manually provided webhook URL.
        :return: Webhook URL string to use.
        :raises ValueError: When neither source provides a URL.
        """
        if webhook_url:
            return webhook_url

        if conn:
            extra = conn.extra_dejson
            url = extra.get("webhook_url", "")
            if url:
                return url
            # Some users store the webhook URL directly in the host field
            if conn.host:
                return conn.host

        raise ValueError(
            "Cannot get Teams webhook URL: No valid webhook_url or teams_conn_id supplied."
        )

    def build_teams_payload(
        self,
        *,
        message: str | None,
        card: AdaptiveCard | None = None,
    ) -> str:
        """
        Build a valid Microsoft Teams webhook JSON payload.

        Teams expects a ``{ "type": "message", "attachments": [...] }`` wrapper
        around an Adaptive Card, or a plain ``{ "text": "..." }`` for simple
        messages.  When both a *message* and a *card* are supplied the card
        takes precedence and the message is ignored.

        :param message: Plain-text fallback message (max 28 KB in practice).
        :param card: An :class:`~teserak.airflow.providers.teams.notifications.adaptive_card.AdaptiveCard` object.
        :return: JSON-encoded payload string.
        """
        if card is not None:
            # Ensure required Adaptive Card fields are present
            if "$schema" not in card:
                card = dict(card)  # type: ignore[misc]
                card["$schema"] = _ADAPTIVE_CARD_SCHEMA
            if "version" not in card:
                card["version"] = _ADAPTIVE_CARD_VERSION

            payload: dict[str, Any] = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": card,
                    }
                ],
            }
        else:
            if not message:
                raise ValueError("Either a message or a card must be provided.")
            payload = {"text": message}

        return json.dumps(payload)


class TeamsWebhookHook(HttpHook):
    """
    Hook for posting messages to Microsoft Teams via Incoming Webhooks.

    Takes a Teams connection ID whose **Extra** field should contain the
    webhook URL::

        {"webhook_url": "https://...webhook.office.com/webhookb2/..."}

    Alternatively pass *webhook_url* directly to skip the connection lookup.

    Each call to :meth:`execute` sends a *POST* request to the webhook endpoint
    with either a plain-text message or a fully-typed
    :class:`~teserak.airflow.providers.teams.notifications.adaptive_card.AdaptiveCard`
    payload.

    :param teams_conn_id: Airflow connection ID of type ``teams``.
    :param webhook_url: Explicit webhook URL (overrides connection setting).
    :param message: Plain-text message to send.
    :param card: Adaptive Card payload; takes precedence over *message*.
    :param proxy: Optional HTTP proxy URL.
    """

    conn_name_attr = "teams_conn_id"
    default_conn_name = "teams_default"
    conn_type = "teams"
    hook_name = "Microsoft Teams"

    @classmethod
    def get_connection_form_widgets(cls) -> dict[str, Any]:
        """Return connection widgets to add to the Teams connection form."""
        from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
        from flask_babel import lazy_gettext
        from wtforms import StringField
        from wtforms.validators import Optional

        return {
            "webhook_url": StringField(
                lazy_gettext("Webhook URL"),
                widget=BS3TextFieldWidget(),
                validators=[Optional()],
                default=None,
            ),
        }

    def __init__(
        self,
        teams_conn_id: str | None = None,
        webhook_url: str | None = None,
        message: str | None = None,
        card: AdaptiveCard | None = None,
        proxy: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._handler = TeamsCommonHandler()
        self.teams_conn_id = teams_conn_id
        self.message = message
        self.card = card
        self.proxy = proxy
        self.webhook_url = self._resolve_webhook_url(teams_conn_id, webhook_url)

    def _resolve_webhook_url(
        self, teams_conn_id: str | None, webhook_url: str | None
    ) -> str:
        """
        Return the webhook URL, resolving from connection if needed.

        :param teams_conn_id: Airflow connection ID.
        :param webhook_url: Explicit webhook URL.
        :return: Resolved webhook URL.
        """
        conn = None
        if not webhook_url and teams_conn_id:
            conn = self.get_connection(teams_conn_id)
        return self._handler.get_webhook_url(conn, webhook_url)

    def execute(self) -> None:
        """Execute the Teams webhook POST request."""
        proxies: dict[str, str] = {}
        if self.proxy:
            proxies = {"https": self.proxy}

        payload = self._handler.build_teams_payload(
            message=self.message,
            card=self.card,
        )
        self.run(
            endpoint=self.webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            extra_options={"proxies": proxies},
        )
