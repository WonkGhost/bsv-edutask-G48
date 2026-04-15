import pytest
from unittest.mock import MagicMock

from src.controllers.usercontroller import UserController


# ---------------------------------------------------------------------------
# Fixture: a UserController with a mocked DAO
# ---------------------------------------------------------------------------

@pytest.fixture
def sut():
    """Return a UserController whose DAO is fully mocked."""
    mock_dao = MagicMock()
    controller = UserController(dao=mock_dao)
    return controller

# ---------------------------------------------------------------------------
# TC1 – Invalid email: plain string without '@'
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_invalid_email_no_at_raises_value_error(sut):
    """An email string without '@' must raise ValueError."""
    with pytest.raises(ValueError, match="invalid email address"):
        sut.get_user_by_email("notanemail") 

# ---------------------------------------------------------------------------
# TC2 – Invalid email: empty string
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_invalid_email_empty_string_raises_value_error(sut):
    """An empty string is not a valid email and must raise ValueError."""
    with pytest.raises(ValueError, match="invalid email address"):
        sut.get_user_by_email("")

# ---------------------------------------------------------------------------
# TC3 – Get user by email
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_user_by_email_calls_dao(sut):
    """Get user by email calls the DAO find method with the given email."""
    # Arrange
    email = "test@test.com"
    # Act
    sut.get_user_by_email(email)
    # Assert
    sut.dao.find.assert_called_once_with({'email': email})