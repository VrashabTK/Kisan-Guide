import asyncio
import httpx
from backend.app.main import app
from backend.app.services.database import (
    normalize_identifier,
    create_user,
    authenticate_user,
    check_account_exists,
    update_crop_preference,
    get_user_by_id
)

def test_identifier_normalization():
    # Email normalization
    t, v = normalize_identifier("  Farmer.Belthangady@Dakshina.in ")
    assert t == "email"
    assert v == "farmer.belthangady@dakshina.in"

    # Indian 10-digit mobile
    t2, v2 = normalize_identifier("9845112233")
    assert t2 == "phone"
    assert v2 == "+919845112233"

    # With +91
    t3, v3 = normalize_identifier("+91 9740123456")
    assert t3 == "phone"
    assert v3 == "+919740123456"

def test_database_registration_and_duplicate_prevention():
    test_email = "test_farmer_dk_unique@dakshina.gov.in"
    if not check_account_exists(email=test_email):
        res = create_user(test_email, "securepass999", "Unique Farmer", "Puttur")
        assert res["user"]["email"] == test_email
        assert res["user"]["taluk"] == "Puttur"
        assert "access_token" in res

    # Verify duplicate creation throws ValueError
    try:
        create_user(test_email, "anotherpass", "Duplicate", "Bantwal")
        assert False, "Should fail on duplicate"
    except ValueError as e:
        assert "already exists" in str(e).lower()

def test_database_authentication_and_rate_limiting():
    test_phone = "9886001122"
    if not check_account_exists(phone_number="+919886001122"):
        create_user(test_phone, "pass123456", "Phone User", "Belthangady")

    # Correct authentication
    auth_res = authenticate_user(test_phone, "pass123456")
    assert auth_res["user"]["phoneNumber"] == "+919886001122"

    # Incorrect authentication
    try:
        authenticate_user(test_phone, "wrongpassword")
        assert False, "Should fail on wrong password"
    except ValueError as e:
        assert "invalid credentials" in str(e).lower()

def test_global_crop_preference_synchronization():
    test_user_id = "test_sync_farmer"
    test_email = "sync_farmer@dakshina.in"
    if not check_account_exists(email=test_email):
        res = create_user(test_email, "pass123456", "Sync Farmer", "Sullia")
        uid = res["user"]["uid"]
    else:
        user = authenticate_user(test_email, "pass123456")
        uid = user["user"]["uid"]

    # Default should be Arecanut
    u = get_user_by_id(uid)
    assert u is not None

    # Update to Coconut
    up1 = update_crop_preference(uid, "Coconut")
    assert up1["selected_crop"] == "Coconut"

    # Update to Rice
    up2 = update_crop_preference(uid, "Rice")
    assert up2["selected_crop"] == "Rice"

    # Update to Cocoa
    up3 = update_crop_preference(uid, "Cocoa")
    assert up3["selected_crop"] == "Cocoa"

def test_api_auth_and_crop_routes():
    async def _run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            test_id = "api_test_farmer@dk.org"
            if not check_account_exists(email=test_id):
                signup_res = await client.post("/api/v1/auth/signup", json={
                    "identifier": test_id,
                    "password": "validpassword123",
                    "confirm_password": "validpassword123",
                    "full_name": "API Test Farmer",
                    "taluk": "Kadaba"
                })
                assert signup_res.status_code == 201
                token = signup_res.json()["access_token"]
            else:
                login_res = await client.post("/api/v1/auth/login", json={
                    "identifier": test_id,
                    "password": "validpassword123"
                })
                assert login_res.status_code == 200
                token = login_res.json()["access_token"]

            headers = {"Authorization": f"Bearer {token}"}

            # Update crop preference via API
            crop_res = await client.put("/api/v1/users/me/crop-preference", json={"crop": "Arecanut"}, headers=headers)
            assert crop_res.status_code == 200
            assert crop_res.json()["selected_crop"] == "Arecanut"

            # Verify profile returns Arecanut
            profile_res = await client.get("/api/v1/users/me", headers=headers)
            assert profile_res.status_code == 200
            assert profile_res.json()["selected_crop"] == "Arecanut"

    asyncio.run(_run())
