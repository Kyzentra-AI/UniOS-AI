
import httpx
import pytest

from app.core.aiml2_client import (
    AIML2Client,
    AIML2ClientError,
)


# Preserve the original HTTPX Client before mocking it.
OriginalHTTPXClient = httpx.Client


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv(
        "AIML2_BASE_URL",
        "https://aiml2-test.example.com",
    )
    return AIML2Client()


def install_mock_transport(monkeypatch, handler):
    def mock_client(**kwargs):
        return OriginalHTTPXClient(
            transport=httpx.MockTransport(handler),
            **kwargs,
        )

    monkeypatch.setattr(
        "app.core.aiml2_client.httpx.Client",
        mock_client,
    )


def test_all_four_api_methods(client, monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)

        if request.url.path.endswith("/build/recommend"):
            return httpx.Response(
                200,
                json={
                    "learner_id": "learner-123",
                    "recommendations": [
                        {"title": "Test Project"}
                    ],
                    "recommendation_rationale": "Test rationale",
                },
            )

        return httpx.Response(
            200,
            json={
                "reply": "Test successful",
                "content": {},
                "summary": "Test summary",
                "findings": [],
                "suggestions": [],
                "action_items": [],
            },
        )

    install_mock_transport(monkeypatch, handler)

    payload = {
        "intent": "guidance",
        "message": "Help me",
    }

    client.generate_resume(payload)
    client.analyze_ats(payload)
    client.coach_build(payload)
    client.recommend_builds("learner-123")

    assert len(calls) == 4

    assert calls[0].url.path == (
        "/api/v1/kie/career/resume/generate"
    )
    assert calls[1].url.path == (
        "/api/v1/kie/career/ats/analyze"
    )
    assert calls[2].url.path == (
        "/api/v1/kie/build/coach"
    )
    assert calls[3].url.path == (
        "/api/v1/kie/build/recommend"
    )

    assert all(request.method == "POST" for request in calls[:3])
    assert calls[3].method == "GET"

    assert calls[3].url.params["learner_id"] == "learner-123"


def test_http_error_is_converted(client, monkeypatch):
    def handler(request):
        return httpx.Response(
            503,
            json={"detail": "Service unavailable"},
        )

    install_mock_transport(monkeypatch, handler)

    with pytest.raises(AIML2ClientError) as exc_info:
        client.coach_build(
            {
                "intent": "guidance",
                "message": "Help me",
            }
        )

    assert exc_info.value.status_code == 503


def test_missing_base_url_raises_error(monkeypatch):
    monkeypatch.delenv(
        "AIML2_BASE_URL",
        raising=False,
    )

    client = AIML2Client()

    with pytest.raises(AIML2ClientError):
        client.coach_build(
            {
                "intent": "guidance",
                "message": "Help me",
            }
        )
