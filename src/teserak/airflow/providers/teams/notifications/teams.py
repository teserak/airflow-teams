from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from airflow.providers.common.compat.notifier import BaseNotifier
from teserak.airflow.providers.teams.hooks.teams_webhook import TeamsWebhookHook
from teserak.airflow.providers.teams.version_compat import AIRFLOW_V_3_1_PLUS

if TYPE_CHECKING:
    from teserak.airflow.providers.teams.notifications.adaptive_card import AdaptiveCard

AIRFLOW_ICON_URL: str = (
    "https://raw.githubusercontent.com/apache/airflow/main/airflow-core/src/airflow/ui/public/pin_100.png"
)


class TeamsNotifier(BaseNotifier):
    """
    Microsoft Teams :class:`~airflow.providers.common.compat.notifier.BaseNotifier`.

    Sends a notification to a Microsoft Teams channel via an Incoming Webhook.
    Can be used as an ``on_failure_callback``, ``on_success_callback``, or any
    other Airflow notification hook.

    Provides both a simple text message and a rich
    :class:`~teserak.airflow.providers.teams.notifications.adaptive_card.AdaptiveCard`
    — when *card* is supplied it takes precedence over *text*.

    :param teams_conn_id: Airflow connection ID of type ``teams`` with the
        webhook URL stored in the Extra field as ``{"webhook_url": "..."}``.
    :param text: Plain-text notification message (templated).
    :param card: Adaptive Card payload (templated). Takes precedence over *text*.
    :param proxy: Optional HTTP proxy URL.

    Example — failure notifier with ready-made card::

        from teserak.airflow.providers.teams.notifications.teams import TeamsNotifier
        from teserak.airflow.providers.teams.notifications.adaptive_card import build_failure_card

        with DAG(
            dag_id="my_dag",
            on_failure_callback=TeamsNotifier(
                teams_conn_id="teams_default",
                card=build_failure_card(
                    dag_id="my_dag",
                    log_url="https://airflow.example.com/log",
                ),
            ),
        ):
            ...
    """

    template_fields: tuple[str, ...] = ("teams_conn_id", "text", "card")

    def __init__(
        self,
        teams_conn_id: str = "teams_default",
        text: str = "",
        card: AdaptiveCard | None = None,
        proxy: str | None = None,
        **kwargs: Any,
    ) -> None:
        if AIRFLOW_V_3_1_PLUS:
            # Support for passing context was added in Airflow 3.1.0
            super().__init__(**kwargs)
        else:
            super().__init__()
        self.teams_conn_id = teams_conn_id
        self.text = text
        self.card = card
        self.proxy = proxy

    @cached_property
    def hook(self) -> TeamsWebhookHook:
        """Return a configured :class:`TeamsWebhookHook`."""
        return TeamsWebhookHook(teams_conn_id=self.teams_conn_id, proxy=self.proxy)

    def notify(self, context: Any) -> None:
        """
        Send a message or Adaptive Card to a Teams channel.

        :param context: The Airflow task execution context.
        """
        self.hook.message = self.text
        self.hook.card = self.card
        self.hook.execute()

    # async_notify deliberately omitted: Teams webhooks are straightforward
    # HTTP POSTs; the async path adds complexity without measurable benefit
    # for this use-case.  Add it when async support is needed.
