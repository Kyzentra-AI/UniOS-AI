
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("AIML2_BASE_URL", "").rstrip("/")

TIMEOUT = httpx.Timeout(
    connect=10.0,
    read=45.0,
    write=15.0,
    pool=5.0,
)


def verify(client, name, method, endpoint, **kwargs):
    print(f"\nTesting {name}...")

    try:
        response = client.request(
            method,
            f"{BASE_URL}{endpoint}",
            **kwargs,
        )

        print("HTTP Status:", response.status_code)

        try:
            data = response.json()
            print("Response:", data)
        except ValueError:
            print("Response:", response.text)
            data = {}

        if response.is_success:
            print(f"{name}: PASSED")
            return True

        print(f"{name}: FAILED")
        return False

    except httpx.RequestError as exc:
        print(f"{name}: CONNECTION ERROR - {exc}")
        return False


def main():
    if not BASE_URL:
        print("AIML2_BASE_URL is missing from .env")
        return

    print("AI/ML-2 LIVE INTEGRATION TEST")
    print("Service:", BASE_URL)

    results = {}

    with httpx.Client(timeout=TIMEOUT) as client:

        results["Build Coach"] = verify(
            client,
            "Build Coach",
            "POST",
            "/api/v1/kie/build/coach",
            json={
                "intent": "guidance",
                "message": "Explain binary search in Python.",
                "context": "Computer Science student",
                "project_context": {
                    "id": "integration-001",
                    "title": "Python Algorithms Project",
                    "type": "code_project",
                    "status": "in_progress",
                    "skills": ["Python", "DSA"],
                },
            },
        )

        results["Resume Generation"] = verify(
            client,
            "Resume Generation",
            "POST",
            "/api/v1/kie/career/resume/generate",
            json={
                "requestId": "integration-resume-001",
                "learnerId": "integration-test-learner",
                "title": "Python Full Stack Developer",
                "source": "manual",
                "preferences": {
                    "targetRole": "Python Full Stack Developer",
                    "tone": "professional",
                },
                "content": {
                    "skills": ["Python", "React", "FastAPI"],
                    "education": [],
                    "experience": [],
                    "projects": [],
                    "achievements": [],
                },
                "careerContext": {
                    "learnerId": "integration-test-learner",
                    "learner": {
                        "skills": ["Python", "React", "FastAPI"],
                        "experience": "",
                    },
                },
            },
        )

        results["ATS Analysis"] = verify(
            client,
            "ATS Analysis",
            "POST",
            "/api/v1/kie/career/ats/analyze",
            json={
                "requestId": "integration-ats-001",
                "learnerId": "integration-test-learner",
                "document": {
                    "fileName": "sample-resume.pdf",
                    "fileType": "pdf",
                    "pageCount": 1,
                    "extractedCharacterCount": 120,
                },
                "extractedText": (
                    "Python developer with React and FastAPI "
                    "project experience."
                ),
                "ruleScore": {
                    "value": 75.5,
                    "maxValue": 100.0,
                    "methodology": "defined-rule-based-checks",
                    "methodologyVersion": "1.0",
                },
                "ruleFindings": [],
            },
        )

        results["Build Recommendations"] = verify(
            client,
            "Build Recommendations",
            "GET",
            "/api/v1/kie/build/recommend",
            params={
                "learner_id": "integration-test-learner",
            },
        )

    print("\n========== FINAL RESULTS ==========")

    for name, passed in results.items():
        print(f"{name}: {'PASSED' if passed else 'FAILED'}")

    total = sum(results.values())
    print(f"\nLIVE ENDPOINTS: {total}/4 PASSED")


if __name__ == "__main__":
    main()
