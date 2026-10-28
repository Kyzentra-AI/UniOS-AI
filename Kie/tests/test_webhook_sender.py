
from unittest.mock import MagicMock

import httpx

from app.core.webhook import BackendWebhookSender


def make_sender(monkeypatch):
    monkeypatch.setenv("BACKEND_BASE_URL", "https://backend.example.com/")
    monkeypatch.setenv("KIE_WEBHOOK_SECRET", "test-secret")
    return BackendWebhookSender()


def test_send_questions_posts_correct_payload_and_authentication(
    monkeypatch,
):
    sender = make_sender(monkeypatch)
    response = MagicMock(status_code=200, text="OK")
    client = MagicMock()
    client.__enter__.return_value = client
    client.post.return_value = response

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client)

    result = sender.send_questions(
        "learner-123",
        [{"question_id": "q1", "text": "What is your goal?"}],
    )

    assert result is True
    client.post.assert_called_once_with(
        "https://backend.example.com/api/v1/onboarding/kie/webhook/questions",
        json={
            "user_id": "learner-123",
            "questions": [
                {"question_id": "q1", "text": "What is your goal?"}
            ],
        },
        headers={
            "Content-Type": "application/json",
            "X-Kie-Signature": "test-secret",
        },
    )


def test_send_resolved_context_posts_correct_payload(monkeypatch):
    sender = make_sender(monkeypatch)
    response = MagicMock(status_code=204, text="")
    client = MagicMock()
    client.__enter__.return_value = client
    client.post.return_value = response

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client)

    result = sender.send_resolved_context(
        "learner-123",
        {"career_goal": "Python developer"},
    )

    assert result is True
    client.post.assert_called_once_with(
        "https://backend.example.com/api/v1/onboarding/kie/webhook/resolved",
        json={
            "user_id": "learner-123",
            "new_context": {"career_goal": "Python developer"},
        },
        headers={
            "Content-Type": "application/json",
            "X-Kie-Signature": "test-secret",
        },
    )


def test_webhook_returns_false_for_http_error(monkeypatch):
    sender = make_sender(monkeypatch)
    response = MagicMock(status_code=500, text="Internal Server Error")
    client = MagicMock()
    client.__enter__.return_value = client
    client.post.return_value = response

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client)

    result = sender.send_questions("learner-123", [])

    assert result is False


def test_webhook_returns_false_for_connection_error(monkeypatch):
    sender = make_sender(monkeypatch)
    client = MagicMock()
    client.__enter__.return_value = client
    client.post.side_effect = httpx.ConnectError(
        "Backend unavailable",
        request=httpx.Request(
            "POST",
            "https://backend.example.com/api/v1/onboarding/kie/webhook/questions",
        ),
    )

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client)

    result = sender.send_questions("learner-123", [])

    assert result is False


def test_webhook_returns_false_when_configuration_is_missing(monkeypatch):
    monkeypatch.delenv("BACKEND_BASE_URL", raising=False)
    monkeypatch.delenv("KIE_WEBHOOK_SECRET", raising=False)

    sender = BackendWebhookSender()

    result = sender.send_questions("learner-123", [])

    assert result is False
