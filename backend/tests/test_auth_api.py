"""
VERIFAI - Integration Tests for Authentication API & Audit Trails
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    # 1. Register
    reg_payload = {
        "email": "researcher@verifai.io",
        "password": "SecurePassword123!",
        "full_name": "Dr. Alex Rivera"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_json = reg_res.json()
    assert reg_json["success"] is True
    assert "access_token" in reg_json["data"]
    assert reg_json["data"]["user"]["email"] == "researcher@verifai.io"

    # 2. Duplicate registration rejection
    dup_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 400
    assert dup_res.json()["success"] is False

    # 3. Login
    login_payload = {
        "email": "researcher@verifai.io",
        "password": "SecurePassword123!"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    assert token is not None

    # 4. Fetch Profile with Bearer Token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["data"]["full_name"] == "Dr. Alex Rivera"

    # 5. Check Audit Logs
    audit_res = await client.get("/api/v1/audit/logs", headers=headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()["data"]["logs"]
    assert len(logs) >= 2  # USER_REGISTER and USER_LOGIN events recorded
    assert any(log["event_type"] == "USER_REGISTER" for log in logs)
    assert any(log["event_type"] == "USER_LOGIN" for log in logs)
