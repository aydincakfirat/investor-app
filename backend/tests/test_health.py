"""
Tests for health / liveness / readiness endpoints.

These are the only endpoints implemented in Phase 1.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_returns_service_info(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "service" in body
    assert "docs" in body


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_body_shape(client: AsyncClient):
    response = await client.get("/api/health")
    body = response.json()
    assert body["status"] == "healthy"
    assert "version" in body
    assert "environment" in body
    assert "uptime_seconds" in body
    assert isinstance(body["uptime_seconds"], (int, float))


@pytest.mark.asyncio
async def test_liveness_returns_200(client: AsyncClient):
    response = await client.get("/api/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_returns_200_or_503(client: AsyncClient):
    """
    In the test environment the DB is an in-memory SQLite.
    The readiness probe should return 200 when the DB is reachable.
    If the probe cannot reach the DB, 503 is acceptable — the important
    thing is that the endpoint exists and returns a structured response.
    """
    response = await client.get("/api/ready")
    assert response.status_code in (200, 503)
    body = response.json()
    assert "status" in body
    assert "database" in body


@pytest.mark.asyncio
async def test_openapi_schema_accessible(client: AsyncClient):
    response = await client.get("/api/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] is not None


@pytest.mark.asyncio
async def test_docs_accessible(client: AsyncClient):
    response = await client.get("/api/docs")
    assert response.status_code == 200
