"""
TUDOaqui - pytest conftest for isolated tests
"""
import pytest


@pytest.fixture(scope="session")
def event_loop_policy():
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


def pytest_collection_modifyitems(config, items):
    """Ensure all async tests use session scope loop."""
    for item in items:
        item.add_marker(pytest.mark.asyncio(loop_scope="session"))
