from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app, follow_redirects=False)


def test_root_redirect():
    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check that each activity has required fields
    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_success():
    # Arrange
    email = "teststudent@mergington.edu"
    activity = "Basketball Team"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]

    # Verify
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity]["participants"]


def test_signup_activity_not_found():
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistentActivity"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_signup_already_signed_up():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_delete_participant_success():
    # Arrange
    email = "deletetest@mergington.edu"
    activity = "Basketball Team"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]

    # Verify
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data[activity]["participants"]


def test_delete_activity_not_found():
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistentActivity"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_delete_not_signed_up():
    # Arrange
    email = "notsigned@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "not signed up" in result["detail"]
