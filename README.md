# teserak-airflow-providers-teams

Provider package for Microsoft Teams integration with Apache Airflow.

## Installation

```bash
pip install teserak-airflow-providers-teams
```

## Requirements

- Apache Airflow >= 2.11.0
- Python >= 3.10

## Connection Setup

Configure an Airflow connection of type `teams`:

| Field | Description |
|-------|-------------|
| **Connection Id** | e.g. `teams_default` |
| **Connection Type** | `teams` |
| **Host** | (leave empty) |
| **Extra** | `{"webhook_url": "https://...webhook.office.com/..."}` |

You can also pass the `webhook_url` directly to the hook/operator without a connection.

Teams uses **Incoming Webhooks** — create one via:
- **Microsoft Teams**: Apps → Incoming Webhooks → configure for a channel
- **Power Automate Workflows** (recommended, replaces older Office 365 connectors)

## Usage

### Hook

```python
from teserak.airflow.providers.teams.hooks.teams_webhook import TeamsWebhookHook
from teserak.airflow.providers.teams.notifications.adaptive_card import (
    AdaptiveCard,
    TextBlock,
    build_success_card,
)

hook = TeamsWebhookHook(
    teams_conn_id="teams_default",
    message="DAG finished successfully!",
)
hook.execute()

# With Adaptive Card
card = build_success_card(
    dag_id="my_dag",
    task_id="my_task",
    execution_date="2024-01-15T10:30:00Z",
    log_url="https://airflow.example.com/log",
)
hook = TeamsWebhookHook(teams_conn_id="teams_default", card=card)
hook.execute()
```

### Operator

```python
from teserak.airflow.providers.teams.operators.teams_webhook import TeamsWebhookOperator

notify = TeamsWebhookOperator(
    task_id="send_teams_message",
    teams_conn_id="teams_default",
    message="Pipeline {{ dag.dag_id }} finished at {{ ts }}",
)
```

### Notifier (on_failure_callback / on_success_callback)

```python
from teserak.airflow.providers.teams.notifications.teams import TeamsNotifier
from teserak.airflow.providers.teams.notifications.adaptive_card import (
    build_failure_card,
    build_success_card,
)

with DAG(
    dag_id="my_pipeline",
    on_failure_callback=TeamsNotifier(
        teams_conn_id="teams_default",
        card=build_failure_card(
            dag_id="my_pipeline",
            log_url="https://airflow.example.com/log",
        ),
    ),
    on_success_callback=TeamsNotifier(
        teams_conn_id="teams_default",
        card=build_success_card(
            dag_id="my_pipeline",
            log_url="https://airflow.example.com/log",
        ),
    ),
):
    ...
```

You can also use a plain text message instead of a card:

```python
with DAG(
    dag_id="my_pipeline",
    on_failure_callback=TeamsNotifier(
        teams_conn_id="teams_default",
        text="DAG {{ dag.dag_id }} failed at {{ ts }}!",
    ),
):
    ...
```

### Ready-made Success / Failure Cards

```python
from teserak.airflow.providers.teams.notifications.adaptive_card import (
    build_success_card,
    build_failure_card,
)

# Success card — green header, checkmark, facts with DAG/task/time/log URL
success_card = build_success_card(
    dag_id="my_dag",
    task_id="my_task",
    execution_date="2024-01-15T10:30:00Z",
    log_url="https://airflow.example.com/log",
)

# Failure card — red header, cross, exception details
failure_card = build_failure_card(
    dag_id="my_dag",
    task_id="my_task",
    execution_date="2024-01-15T10:30:00Z",
    exception="ValueError: unexpected value",
    log_url="https://airflow.example.com/log",
)
```

## Adaptive Card Structure

Teams uses [Adaptive Cards](https://adaptivecards.io/) instead of Discord's Embed objects.
All types are fully typed as `TypedDict`:

- `AdaptiveCard` — root card (body, actions, $schema, version)
- `TextBlock` — text elements with size/weight/color/wrap
- `FactSet` / `Fact` — key-value pairs (analogous to Discord EmbedField)
- `Image` — image element
- `ColumnSet` / `Column` — multi-column layout
- `Container` — grouping container with optional background
- `ActionOpenUrl` / `ActionSet` — clickable button actions
