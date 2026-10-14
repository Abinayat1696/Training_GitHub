from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_signup_rejects_duplicate_registration():
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    # Reset state for deterministic test
    activities[activity_name]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]

    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_them_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    activities[activity_name]["participants"] = [
        email,
        "daniel@mergington.edu",
    ]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}",
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    activities[activity_name]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}",
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
