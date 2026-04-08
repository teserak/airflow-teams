from __future__ import annotations

import pytest


@pytest.fixture
def teams_connection():
    """Return a minimal dict representing an Airflow Teams connection extra."""
    return {"webhook_url": "https://example.webhook.office.com/webhookb2/abc/IncomingWebhook/123/xyz"}
