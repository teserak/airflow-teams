from __future__ import annotations

import json
from unittest import mock

import pytest

from airflow.models.dag import DAG
from airflow.utils import timezone
from teserak.airflow.providers.teams.operators.teams_webhook import TeamsWebhookOperator

DEFAULT_DATE = timezone.datetime(2024, 1, 15)

WEBHOOK_URL = "https://example.webhook.office.com/webhookb2/abc/IncomingWebhook/123/xyz"

_CONFIG = {
    "teams_conn_id": "teams_default",
    "webhook_url": WEBHOOK_URL,
    "message": "Hello from {{ dag.dag_id }}",
    "proxy": "https://proxy.example.com:8888",
}


class TestTeamsWebhookOperator:
    """Tests for :class:`TeamsWebhookOperator`."""

    def setup_method(self):
        args = {"owner": "airflow", "start_date": DEFAULT_DATE}
        self.dag = DAG("test_dag_id", schedule=None, default_args=args)

    def test_sets_attributes_correctly(self):
        operator = TeamsWebhookOperator(task_id="teams_task", dag=self.dag, **_CONFIG)
        assert operator.teams_conn_id == _CONFIG["teams_conn_id"]
        assert operator.webhook_url == _CONFIG["webhook_url"]
        assert operator.message == _CONFIG["message"]
        assert operator.proxy == _CONFIG["proxy"]

    def test_missing_conn_and_url_raises(self):
        with pytest.raises(Exception, match="No valid Teams connection supplied"):
            TeamsWebhookOperator(
                task_id="bad_task",
                dag=self.dag,
                message="test",
            )

    def test_hook_property_returns_hook(self):
        from teserak.airflow.providers.teams.hooks.teams_webhook import TeamsWebhookHook

        with mock.patch.object(TeamsWebhookHook, "__init__", return_value=None):
            operator = TeamsWebhookOperator(
                task_id="teams_task",
                dag=self.dag,
                teams_conn_id="teams_default",
                webhook_url=WEBHOOK_URL,
                message="hi",
            )
            hook = operator.hook
            assert isinstance(hook, TeamsWebhookHook)

    def test_execute_calls_hook_execute(self):
        operator = TeamsWebhookOperator(
            task_id="teams_task",
            dag=self.dag,
            teams_conn_id="teams_default",
            webhook_url=WEBHOOK_URL,
            message="hello",
        )
        with mock.patch(
            "teserak.airflow.providers.teams.operators.teams_webhook.TeamsWebhookHook.execute"
        ) as mock_execute, mock.patch(
            "teserak.airflow.providers.teams.hooks.teams_webhook.TeamsWebhookHook.get_connection"
        ):
            operator.execute(context=mock.MagicMock())
            mock_execute.assert_called_once()

    def test_template_fields_include_message(self):
        assert "message" in TeamsWebhookOperator.template_fields
        assert "webhook_url" in TeamsWebhookOperator.template_fields
