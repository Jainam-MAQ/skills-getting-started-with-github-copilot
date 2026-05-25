"""
Tests for the Mergington High School API

Tests follow the Arrange-Act-Assert (AAA) pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a TestClient instance for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all available activities.
        
        AAA Pattern:
        - Arrange: Create test client
        - Act: Send GET request to /activities
        - Assert: Verify response status is 200 and contains all expected activities
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Workshop",
            "Drama Club",
            "Debate Team",
            "Science Club",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == len(expected_activities)
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_response_structure(self, client):
        """
        Test that each activity in the response has the correct structure.
        
        AAA Pattern:
        - Arrange: Create test client
        - Act: Send GET request to /activities
        - Assert: Verify each activity has required fields (description, schedule, max_participants, participants)
        """
        # Arrange
        required_fields = {
            "description",
            "schedule",
            "max_participants",
            "participants",
        }

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"Activity {activity_name} is not a dict"
            assert activity_data.keys() == required_fields, (
                f"Activity {activity_name} has incorrect fields. "
                f"Expected {required_fields}, got {activity_data.keys()}"
            )
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["description"], str)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """
        Test successful signup for an activity.
        
        AAA Pattern:
        - Arrange: Create test client, select an activity, get initial participant count
        - Act: Send POST request with new email to signup
        - Assert: Verify status is 200, response message is correct, participant count increased
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Get initial state
        get_response = client.get("/activities")
        initial_participants = get_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {new_email} for {activity_name}"
        }
        
        # Verify participant was added
        get_response = client.get("/activities")
        updated_participants = get_response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count + 1
        assert new_email in updated_participants

    def test_signup_activity_not_found(self, client):
        """
        Test signup with a non-existent activity.
        
        AAA Pattern:
        - Arrange: Create test client, prepare non-existent activity name
        - Act: Send POST request with invalid activity
        - Assert: Verify status is 404 and error detail is correct
        """
        # Arrange
        invalid_activity_name = "NonExistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_email(self, client):
        """
        Test signup with an email already signed up for the activity.
        
        AAA Pattern:
        - Arrange: Create test client, select activity and get an existing participant email
        - Act: Send POST request with duplicate email
        - Assert: Verify status is 400 and error detail indicates already signed up
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Get an existing participant
        get_response = client.get("/activities")
        existing_email = get_response.json()[activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_at_capacity_still_allows(self, client):
        """
        Test that signup is allowed even at max capacity (no capacity check in endpoint).
        
        AAA Pattern:
        - Arrange: Create test client, select activity, prepare new email
        - Act: Send POST request for signup
        - Assert: Verify signup succeeds (endpoint has no capacity validation)
        """
        # Arrange
        activity_name = "Programming Class"
        new_email = "anotherstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email},
        )

        # Assert
        # The endpoint does not validate max capacity, so this should succeed
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
