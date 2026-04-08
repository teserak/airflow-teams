from __future__ import annotations

import pytest

from teserak.airflow.providers.teams.notifications.adaptive_card import (
    ActionOpenUrl,
    ActionSet,
    AdaptiveCard,
    Column,
    ColumnSet,
    Container,
    Fact,
    FactSet,
    Image,
    TextBlock,
    build_failure_card,
    build_success_card,
)

_ADAPTIVE_CARD_SCHEMA = "http://adaptivecards.io/schemas/adaptive-card.json"


class TestAdaptiveCardFactories:
    """Tests for :func:`build_success_card` and :func:`build_failure_card`."""

    def test_build_success_card_type(self):
        card = build_success_card(dag_id="my_dag")
        assert card["type"] == "AdaptiveCard"

    def test_build_success_card_has_body(self):
        card = build_success_card(dag_id="my_dag")
        assert "body" in card
        assert len(card["body"]) >= 1

    def test_build_success_card_title_contains_dag_id(self):
        card = build_success_card(dag_id="my_awesome_dag")
        title_block = card["body"][0]
        assert "my_awesome_dag" in title_block["text"]

    def test_build_success_card_color_is_good(self):
        card = build_success_card(dag_id="my_dag")
        title_block = card["body"][0]
        assert title_block["color"] == "good"

    def test_build_success_card_has_checkmark_emoji(self):
        card = build_success_card(dag_id="my_dag")
        title_block = card["body"][0]
        assert "✅" in title_block["text"]

    def test_build_success_card_facts_contain_dag_id(self):
        card = build_success_card(dag_id="my_dag")
        fact_set = card["body"][1]
        assert fact_set["type"] == "FactSet"
        fact_titles = [f["title"] for f in fact_set["facts"]]
        assert "DAG" in fact_titles

    def test_build_success_card_with_all_params(self):
        card = build_success_card(
            dag_id="pipe",
            task_id="my_task",
            execution_date="2024-01-15T10:30:00Z",
            log_url="https://airflow.example.com/log",
        )
        fact_set = card["body"][1]
        fact_titles = [f["title"] for f in fact_set["facts"]]
        assert "Task" in fact_titles
        assert "Execution Date" in fact_titles
        # log_url becomes an action button
        assert "actions" in card
        assert card["actions"][0]["url"] == "https://airflow.example.com/log"

    def test_build_success_card_schema_and_version(self):
        card = build_success_card(dag_id="my_dag")
        assert card["schema"] == _ADAPTIVE_CARD_SCHEMA
        assert "version" in card

    def test_build_failure_card_type(self):
        card = build_failure_card(dag_id="my_dag")
        assert card["type"] == "AdaptiveCard"

    def test_build_failure_card_color_is_attention(self):
        card = build_failure_card(dag_id="my_dag")
        title_block = card["body"][0]
        assert title_block["color"] == "attention"

    def test_build_failure_card_has_cross_emoji(self):
        card = build_failure_card(dag_id="my_dag")
        title_block = card["body"][0]
        assert "❌" in title_block["text"]

    def test_build_failure_card_exception_in_facts(self):
        card = build_failure_card(
            dag_id="my_dag",
            exception="ValueError: something went wrong",
        )
        fact_set = card["body"][1]
        fact_titles = [f["title"] for f in fact_set["facts"]]
        assert "Exception" in fact_titles
        exception_fact = next(f for f in fact_set["facts"] if f["title"] == "Exception")
        assert "ValueError" in exception_fact["value"]

    def test_build_failure_card_with_log_url_adds_action(self):
        card = build_failure_card(dag_id="bad_dag", log_url="https://log.example.com")
        assert "actions" in card
        assert card["actions"][0]["type"] == "Action.OpenUrl"
        assert card["actions"][0]["url"] == "https://log.example.com"

    def test_build_failure_card_without_log_url_no_actions(self):
        card = build_failure_card(dag_id="bad_dag")
        assert "actions" not in card

    def test_build_success_card_without_optional_params(self):
        """Optional parameters should be omitted cleanly."""
        card = build_success_card(dag_id="minimal_dag")
        fact_set = card["body"][1]
        fact_titles = [f["title"] for f in fact_set["facts"]]
        assert "Task" not in fact_titles
        assert "Execution Date" not in fact_titles
        assert "actions" not in card


class TestAdaptiveCardElements:
    """Structural tests for individual Adaptive Card TypedDict elements."""

    def test_text_block_required_fields(self):
        block = TextBlock(type="TextBlock", text="Hello")
        assert block["type"] == "TextBlock"
        assert block["text"] == "Hello"

    def test_fact_set(self):
        facts = [Fact(title="Key", value="Value")]
        fs = FactSet(type="FactSet", facts=facts)
        assert fs["type"] == "FactSet"
        assert fs["facts"][0]["title"] == "Key"

    def test_action_open_url(self):
        action = ActionOpenUrl(type="Action.OpenUrl", title="Click me", url="https://example.com")
        assert action["type"] == "Action.OpenUrl"
        assert action["url"] == "https://example.com"

    def test_image(self):
        img = Image(type="Image", url="https://example.com/img.png", altText="test")
        assert img["type"] == "Image"
        assert img["altText"] == "test"

    def test_column_and_column_set(self):
        col = Column(
            type="Column",
            items=[TextBlock(type="TextBlock", text="col content")],
            width="stretch",
        )
        cs = ColumnSet(type="ColumnSet", columns=[col])
        assert cs["type"] == "ColumnSet"
        assert cs["columns"][0]["width"] == "stretch"

    def test_container(self):
        container = Container(
            type="Container",
            items=[TextBlock(type="TextBlock", text="inside")],
            style="emphasis",
        )
        assert container["type"] == "Container"
        assert container["style"] == "emphasis"
