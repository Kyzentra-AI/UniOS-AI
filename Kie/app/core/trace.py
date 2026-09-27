from uuid import uuid4


def generate_request_id() -> str:
    """Generate a unique ID for a KIE execution request."""
    return f"req_{uuid4().hex}"


def generate_session_id() -> str:
    """Generate a session ID when one is not supplied by the client."""
    return f"ses_{uuid4().hex}"