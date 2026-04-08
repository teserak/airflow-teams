from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from airflow.providers.common.compat.sdk import AirflowException
from airflow.providers.http.operators.http import HttpOperator
from teserak.airflow.providers.teams.hooks.teams_webhook import TeamsWebhookHook

if TYPE_CHECKING:
    from airflow.providers.common.compat.sdk import Context
    from teserak.airflow.providers.teams.notifications.adaptive_card import AdaptiveCard


class TeamsWebhookOperator(HttpOperator):
    """
    Operator for posting messages to Microsoft Teams via Incoming Webhooks.

    Takes a Teams connection ID with the webhook URL stored in the Extra field.
    You may also pass *webhook_url* directly to bypass the connection lookup.

    :param teams_conn_id: Airflow connection ID of type ``teams`` (required unless
        *webhook_url* is provided).
    :param webhook_url: Explicit Teams incoming webhook URL (templated).
    :param message: Plain-text message to send (max ~28 KB) (templated).
    :param card: Adaptive Card payload; takes precedence over *message*.
    :param proxy: Optional HTTP proxy URL for the webhook request.
    """

    template_fields: Sequence[str] = ("message", "webhook_url")

    def __init__(
        self,
        *,
        teams_conn_id: str | None = None,
        webhook_url: str | None = None,
        message: str | None = None,
        card: AdaptiveCard | None = None,
        proxy: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(endpoint=webhook_url, **kwargs)

        if not teams_conn_id and not webhook_url:
            raise AirflowException(
                "No valid Teams connection supplied. "
                "Provide either teams_conn_id or webhook_url."
            )

        self.teams_conn_id = teams_conn_id
        self.webhook_url = webhook_url
        self.message = message
        self.card = card
        self.proxy = proxy

    @property
    def hook(self) -> TeamsWebhookHook:
        """Return a configured :class:`TeamsWebhookHook`."""
        return TeamsWebhookHook(
            teams_conn_id=self.teams_conn_id,
            webhook_url=self.webhook_url,
            message=self.message,
            card=self.card,
            proxy=self.proxy,
        )

    def execute(self, context: Context) -> None:
        """
        Call the :class:`TeamsWebhookHook` to post a message.

        :param context: The Airflow task execution context.
        """
        self.hook.execute()
