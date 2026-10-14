from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_root_redirects_to_activity_page():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert response.json()[expected_activity]["participants"] == activities[expected_activity]["participants"]


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
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
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert activities[activity_name]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
        email,
    ]


def test_signup_rejects_duplicate_registration():
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"
    participants = [email, "daniel@mergington.edu"]
    activities[activity_name]["participants"] = participants.copy()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"] == participants


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


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
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert activities[activity_name]["participants"] == ["daniel@mergington.edu"]


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
    assert activities[activity_name]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_unregister_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}",
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
