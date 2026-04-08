from __future__ import annotations


def get_provider_info():
    return {
        "package-name": "teserak-airflow-providers-teams",
        "name": "Microsoft Teams",
        "description": "`Microsoft Teams <https://www.microsoft.com/en-us/microsoft-teams/>`__\n",
        "integrations": [
            {
                "integration-name": "Microsoft Teams",
                "external-doc-url": "https://www.microsoft.com/en-us/microsoft-teams/group-chat-software",
                "tags": ["service"],
            }
        ],
        "operators": [
            {
                "integration-name": "Microsoft Teams",
                "python-modules": ["teserak.airflow.providers.teams.operators.teams_webhook"],
            }
        ],
        "hooks": [
            {
                "integration-name": "Microsoft Teams",
                "python-modules": ["teserak.airflow.providers.teams.hooks.teams_webhook"],
            }
        ],
        "connection-types": [
            {
                "hook-class-name": "teserak.airflow.providers.teams.hooks.teams_webhook.TeamsWebhookHook",
                "hook-name": "Microsoft Teams",
                "connection-type": "teams",
                "conn-fields": {
                    "webhook_url": {
                        "label": "Webhook URL",
                        "schema": {"type": ["string", "null"]},
                    }
                },
            }
        ],
        "notifications": ["teserak.airflow.providers.teams.notifications.teams.TeamsNotifier"],
    }
