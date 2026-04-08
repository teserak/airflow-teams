"""
Microsoft Teams Adaptive Card structure.

See:
    https://adaptivecards.io/explorer/
    https://learn.microsoft.com/en-us/adaptive-cards/authoring-cards/getting-started
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Union

from typing_extensions import NotRequired, Required, TypedDict

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Literal types
# ---------------------------------------------------------------------------

TextBlockSize = Literal["default", "small", "medium", "large", "extraLarge"]
TextBlockWeight = Literal["default", "lighter", "bolder"]
TextBlockColor = Literal["default", "dark", "light", "accent", "good", "warning", "attention"]
HorizontalAlignment = Literal["left", "center", "right"]
VerticalAlignment = Literal["top", "center", "bottom"]
ImageSize = Literal["auto", "stretch", "small", "medium", "large"]
ImageStyle = Literal["default", "person"]
ContainerStyle = Literal["default", "emphasis", "good", "attention", "warning", "accent"]
ActionStyle = Literal["default", "positive", "destructive"]
Spacing = Literal["none", "small", "default", "medium", "large", "extraLarge", "padding"]


# ---------------------------------------------------------------------------
# Card Element Types
# ---------------------------------------------------------------------------


class TextBlock(TypedDict, total=False):
    """
    TextBlock element — displays text, optionally styled.

    :param type: Must be ``"TextBlock"``.
    :param text: Text to display (required). Supports Markdown.
    :param color: Controls text color.
    :param fontType: Controls which font to use.
    :param horizontalAlignment: Aligns text within its column.
    :param isSubtle: If ``True``, displays text slightly toned down.
    :param maxLines: Limits lines, hiding overflow text.
    :param size: Controls text size.
    :param weight: Controls text weight.
    :param wrap: If ``True``, allows wrapping to multiple lines.
    :param spacing: Controls spacing before this element.
    :param separator: Draws a separator line above the element.

    See:
        https://adaptivecards.io/explorer/TextBlock.html
    """

    type: Required[Literal["TextBlock"]]
    text: Required[str]
    color: TextBlockColor
    fontType: Literal["default", "monospace"]
    horizontalAlignment: HorizontalAlignment
    isSubtle: bool
    maxLines: int
    size: TextBlockSize
    weight: TextBlockWeight
    wrap: bool
    spacing: Spacing
    separator: bool


class Image(TypedDict, total=False):
    """
    Image element.

    :param type: Must be ``"Image"``.
    :param url: The URL of the image (required).
    :param altText: Alternate text used for screen reader.
    :param horizontalAlignment: Aligns image within its column.
    :param size: Controls image size.
    :param style: Controls how the image is displayed.
    :param spacing: Controls spacing before this element.
    :param separator: Draws a separator line above the element.

    See:
        https://adaptivecards.io/explorer/Image.html
    """

    type: Required[Literal["Image"]]
    url: Required[str]
    altText: str
    horizontalAlignment: HorizontalAlignment
    size: ImageSize
    style: ImageStyle
    height: str
    width: str
    spacing: Spacing
    separator: bool


class Fact(TypedDict):
    """
    A single fact (key-value pair) within a :class:`FactSet`.

    :param title: Fact title (name / label).
    :param value: Fact value.

    See:
        https://adaptivecards.io/explorer/FactSet.html
    """

    title: str
    value: str


class FactSet(TypedDict, total=False):
    """
    FactSet element — displays a series of ``Fact`` key-value pairs.

    Analogous to Discord's ``EmbedField`` list.

    :param type: Must be ``"FactSet"``.
    :param facts: List of facts (required).
    :param spacing: Controls spacing before this element.
    :param separator: Draws a separator line above the element.

    See:
        https://adaptivecards.io/explorer/FactSet.html
    """

    type: Required[Literal["FactSet"]]
    facts: Required[list[Fact]]
    spacing: Spacing
    separator: bool


class ActionOpenUrl(TypedDict, total=False):
    """
    Action that opens a URL when clicked.

    :param type: Must be ``"Action.OpenUrl"``.
    :param title: Label for the button.
    :param url: URL to open (required).
    :param style: Controls the button style.

    See:
        https://adaptivecards.io/explorer/Action.OpenUrl.html
    """

    type: Required[Literal["Action.OpenUrl"]]
    title: Required[str]
    url: Required[str]
    style: ActionStyle
    iconUrl: str


class ActionSet(TypedDict, total=False):
    """
    ActionSet element — groups actions inside the card body.

    :param type: Must be ``"ActionSet"``.
    :param actions: List of actions (required).
    :param spacing: Controls spacing before this element.
    :param separator: Draws a separator line above the element.

    See:
        https://adaptivecards.io/explorer/ActionSet.html
    """

    type: Required[Literal["ActionSet"]]
    actions: Required[list[ActionOpenUrl]]
    spacing: Spacing
    separator: bool


# Column/ColumnSet use a forward reference since Column contains ColumnSet items
CardElement = Union[TextBlock, Image, FactSet, ActionSet, "Container", "ColumnSet"]


class Column(TypedDict, total=False):
    """
    A column within a :class:`ColumnSet`.

    :param type: Must be ``"Column"``.
    :param items: Elements inside this column (required).
    :param width: Width as explicit pixel value (``"auto"``, ``"stretch"``, or number).
    :param style: Container style applied to this column.
    :param verticalContentAlignment: Aligns content vertically.

    See:
        https://adaptivecards.io/explorer/Column.html
    """

    type: Required[Literal["Column"]]
    items: Required[list[CardElement]]
    width: str
    style: ContainerStyle
    verticalContentAlignment: VerticalAlignment
    spacing: Spacing
    separator: bool


class ColumnSet(TypedDict, total=False):
    """
    ColumnSet element — side-by-side column layout.

    :param type: Must be ``"ColumnSet"``.
    :param columns: List of columns (required).
    :param spacing: Controls spacing before this element.
    :param separator: Draws a separator line above the element.

    See:
        https://adaptivecards.io/explorer/ColumnSet.html
    """

    type: Required[Literal["ColumnSet"]]
    columns: Required[list[Column]]
    spacing: Spacing
    separator: bool


class Container(TypedDict, total=False):
    """
    Container element — groups a set of elements.

    :param type: Must be ``"Container"``.
    :param items: Elements inside the container (required).
    :param style: Background style.
    :param bleed: If ``True``, the container bleeds through its parent's padding.
    :param spacing: Controls spacing before this element.
    :param separator: Draws a separator line above the element.

    See:
        https://adaptivecards.io/explorer/Container.html
    """

    type: Required[Literal["Container"]]
    items: Required[list[CardElement]]
    style: ContainerStyle
    bleed: bool
    spacing: Spacing
    separator: bool


class AdaptiveCard(TypedDict, total=False):
    """
    Root Adaptive Card object.

    Analogous to Discord's :class:`~teserak.airflow.providers.teams.notifications.adaptive_card.Embed`.

    :param type: Must be ``"AdaptiveCard"``.
    :param body: List of card body elements (required).
    :param actions: Top-level actions (buttons).
    :param schema: JSON schema URI — always
        ``"http://adaptivecards.io/schemas/adaptive-card.json"``.
    :param version: Adaptive Card schema version (e.g. ``"1.5"``).
    :param fallbackText: Text shown if the client cannot render the card.
    :param speak: An SSML snippet describing what should be spoken for this card.

    See:
        https://adaptivecards.io/explorer/AdaptiveCard.html
    """

    type: Required[Literal["AdaptiveCard"]]
    body: Required[list[CardElement]]
    actions: list[ActionOpenUrl]
    schema: str
    version: str
    fallbackText: str
    speak: str


# ---------------------------------------------------------------------------
# Teams message wrapper
# ---------------------------------------------------------------------------


class TeamsAttachment(TypedDict):
    """
    A single attachment wrapping an :class:`AdaptiveCard` for Teams webhooks.

    :param contentType: Always ``"application/vnd.microsoft.card.adaptive"``.
    :param content: The :class:`AdaptiveCard` payload.
    """

    contentType: Literal["application/vnd.microsoft.card.adaptive"]
    content: AdaptiveCard


class TeamsMessage(TypedDict):
    """
    Top-level Teams webhook message payload.

    :param type: Always ``"message"``.
    :param attachments: List of card attachments.
    """

    type: Literal["message"]
    attachments: list[TeamsAttachment]


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

_ADAPTIVE_CARD_SCHEMA = "http://adaptivecards.io/schemas/adaptive-card.json"
_ADAPTIVE_CARD_VERSION = "1.5"


def _make_card(
    title: str,
    title_color: TextBlockColor,
    emoji: str,
    facts: list[Fact],
    log_url: str | None = None,
) -> AdaptiveCard:
    """Build a base Adaptive Card with title, status facts, and optional log link."""
    body: list[CardElement] = [
        TextBlock(
            type="TextBlock",
            text=f"{emoji}  {title}",
            size="large",
            weight="bolder",
            color=title_color,
            wrap=True,
        ),
        FactSet(
            type="FactSet",
            facts=facts,
            spacing="medium",
        ),
    ]
    card: AdaptiveCard = AdaptiveCard(
        type="AdaptiveCard",
        body=body,
        schema=_ADAPTIVE_CARD_SCHEMA,
        version=_ADAPTIVE_CARD_VERSION,
    )
    if log_url:
        card["actions"] = [
            ActionOpenUrl(
                type="Action.OpenUrl",
                title="View Log",
                url=log_url,
                style="positive",
            )
        ]
    return card


def build_success_card(
    dag_id: str,
    task_id: str | None = None,
    execution_date: str | None = None,
    log_url: str | None = None,
) -> AdaptiveCard:
    """
    Build a ready-made success :class:`AdaptiveCard`.

    The card uses a green header with a checkmark emoji and lists DAG/task
    details as a :class:`FactSet`.

    :param dag_id: The DAG identifier.
    :param task_id: Optional task identifier.
    :param execution_date: Optional ISO 8601 execution timestamp.
    :param log_url: Optional URL to the Airflow log viewer.
    :return: An :class:`AdaptiveCard` ready to pass to :class:`~teserak.airflow.providers.teams.hooks.teams_webhook.TeamsWebhookHook`.
    """
    facts: list[Fact] = [Fact(title="DAG", value=dag_id)]
    if task_id:
        facts.append(Fact(title="Task", value=task_id))
    if execution_date:
        facts.append(Fact(title="Execution Date", value=execution_date))
    facts.append(Fact(title="Status", value="Success"))
    return _make_card(
        title=f"DAG Succeeded: {dag_id}",
        title_color="good",
        emoji="✅",
        facts=facts,
        log_url=log_url,
    )


def build_failure_card(
    dag_id: str,
    task_id: str | None = None,
    execution_date: str | None = None,
    exception: str | None = None,
    log_url: str | None = None,
) -> AdaptiveCard:
    """
    Build a ready-made failure :class:`AdaptiveCard`.

    The card uses a red header with a cross emoji and lists DAG/task details
    along with the exception message as a :class:`FactSet`.

    :param dag_id: The DAG identifier.
    :param task_id: Optional task identifier.
    :param execution_date: Optional ISO 8601 execution timestamp.
    :param exception: Optional exception string to include in the card.
    :param log_url: Optional URL to the Airflow log viewer.
    :return: An :class:`AdaptiveCard` ready to pass to :class:`~teserak.airflow.providers.teams.hooks.teams_webhook.TeamsWebhookHook`.
    """
    facts: list[Fact] = [Fact(title="DAG", value=dag_id)]
    if task_id:
        facts.append(Fact(title="Task", value=task_id))
    if execution_date:
        facts.append(Fact(title="Execution Date", value=execution_date))
    facts.append(Fact(title="Status", value="Failed"))
    if exception:
        facts.append(Fact(title="Exception", value=str(exception)))
    return _make_card(
        title=f"DAG Failed: {dag_id}",
        title_color="attention",
        emoji="❌",
        facts=facts,
        log_url=log_url,
    )
