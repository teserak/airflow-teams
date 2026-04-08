from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

from teserak.airflow.providers.teams.notifications.adaptive_card import (
    AdaptiveCard,
    Fact,
    FactSet,
    TextBlock,
    build_failure_card,
    build_success_card,
)
from teserak.airflow.providers.teams.notifications.teams import TeamsNotifier

WEBHOOK_URL = "https://example.webhook.office.com/webhookb2/abc/IncomingWebhook/123/xyz"


@patch(
    "teserak.airflow.providers.teams.notifications.teams.TeamsWebhookHook.execute",
)
def test_teams_notifier_plain_text(mock_execute):
    """Notifier should call hook.execute() with text."""
    notifier = TeamsNotifier(
        teams_conn_id="teams_default",
        text="Pipeline finished!",
    )
    context = MagicMock()
    with patch(
        "teserak.airflow.providers.teams.hooks.teams_webhook.TeamsWebhookHook.get_connection"
    ):
        notifier.notify(context)

    mock_execute.assert_called_once()
    assert notifier.hook.message == "Pipeline finished!"
    assert notifier.hook.card is None


@patch(
    "teserak.airflow.providers.teams.notifications.teams.TeamsWebhookHook.execute",
)
def test_teams_notifier_with_adaptive_card(mock_execute):
    """Notifier should pass the card through to the hook."""
    card: AdaptiveCard = AdaptiveCard(
        type="AdaptiveCard",
        body=[TextBlock(type="TextBlock", text="Test alert")],
    )
    notifier = TeamsNotifier(teams_conn_id="teams_default", card=card)
    context = MagicMock()
    with patch(
        "teserak.airflow.providers.teams.hooks.teams_webhook.TeamsWebhookHook.get_connection"
    ):
        notifier.notify(context)

    mock_execute.assert_called_once()
    assert notifier.hook.card is card


@patch("teserak.airflow.providers.teams.notifications.teams.TeamsWebhookHook")
def test_teams_notifier_templated(mock_hook_cls):
    """Template fields should be rendered before notify executes."""
    notifier = TeamsNotifier(
        teams_conn_id="teams_default",
        text="DAG {{ dag_id }} done",
    )
    assert "text" in TeamsNotifier.template_fields
    assert "teams_conn_id" in TeamsNotifier.template_fields
    assert "card" in TeamsNotifier.template_fields


@patch(
    "teserak.airflow.providers.teams.notifications.teams.TeamsWebhookHook.execute",
)
def test_teams_notifier_success_card(mock_execute):
    """Notifier with a build_success_card should pass the Adaptive Card payload."""
    card = build_success_card(
        dag_id="my_dag",
        task_id="my_task",
        execution_date="2024-01-15T10:30:00Z",
        log_url="https://airflow.example.com/log",
    )
    notifier = TeamsNotifier(teams_conn_id="teams_default", card=card)
    with patch(
        "teserak.airflow.providers.teams.hooks.teams_webhook.TeamsWebhookHook.get_connection"
    ):
        notifier.notify({})
    assert notifier.hook.card is card
    mock_execute.assert_called_once()


@patch(
    "teserak.airflow.providers.teams.notifications.teams.TeamsWebhookHook.execute",
)
def test_teams_notifier_failure_card(mock_execute):
    """Notifier with a build_failure_card should pass the Adaptive Card payload."""
    card = build_failure_card(
        dag_id="my_dag",
        task_id="my_task",
        execution_date="2024-01-15T10:30:00Z",
        exception="ValueError: oops",
        log_url="https://airflow.example.com/log",
    )
    notifier = TeamsNotifier(teams_conn_id="teams_default", card=card)
    with patch(
        "teserak.airflow.providers.teams.hooks.teams_webhook.TeamsWebhookHook.get_connection"
    ):
        notifier.notify({})
    assert notifier.hook.card is card
    mock_execute.assert_called_once()


@patch("teserak.airflow.providers.teams.notifications.teams.TeamsWebhookHook")
def test_teams_notifier_default_conn_id(mock_hook_cls):
    """Default connection ID should be 'teams_default'."""
    notifier = TeamsNotifier()
    assert notifier.teams_conn_id == "teams_default"
