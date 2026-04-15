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
# TC3 – Valid email, one user found: returns that user
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_valid_email_one_user_returns_user(sut):
    """When the DAO returns exactly one user, the function returns it."""
    # Arrange
    user = {"_id": "abc123", "email": "user@test.com"}

    sut.dao.find.return_value = [user]

    # Act
    result = sut.get_user_by_email("user@test.com")

    # Assert
    sut.dao.find.assert_called_once_with({'email': "user@test.com"})
    assert result == user

# ---------------------------------------------------------------------------
# TC4 – Valid email, multiple users found: returns first user
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_email_alredy_exists_returns_first_user(sut, capsys):
    """When the DAO returns multiple users, the function returns the first one."""
    # Arrange
    user1 = {"_id": "abc123", "email": "user@test.com"}
    user2 ={"_id": "def456", "email": "user@test.com"}

    sut.dao.find.return_value = [user1, user2]

    # Act
    result = sut.get_user_by_email("user@test.com")

    # Assert
    captured = capsys.readouterr()
    assert "user@test.com" in captured.out

    sut.dao.find.assert_called_once_with({'email': "user@test.com"})
    assert result == user1

# ---------------------------------------------------------------------------
# TC5 – Valid email, no user found: returns None (EXPECTED TO FAIL)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_valid_email_no_user_returns_none(sut):
    """When the DAO returns no users, the function returns None."""
    # Arrange
    sut.dao.find.return_value = []

    # Act
    result = sut.get_user_by_email("user@test.com")

    # Assert
    sut.dao.find.assert_called_once_with({'email': "user@test.com"})
    assert result is None

# ---------------------------------------------------------------------------
# TC6 valid email, database raises exception
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_valid_email_database_error_raises_exception(sut):
    """When the DAO raises an exception, it should propagate."""
    # Arrange
    sut.dao.find.side_effect = Exception("Database error")
    
    # Act
    with pytest.raises(Exception, match="Database error"):
        sut.get_user_by_email("user@test.com")
    # Assert
    sut.dao.find.assert_called_once_with({'email': "user@test.com"})

# ---------------------------------------------------------------------------
# TC7 EXTRA, testing update()
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_update_wraps_data_in_set_operator(sut):
    """update() should wrap the data dict in {'$set': data} before calling the DAO."""
    # Arrange
    sut.dao.update.return_value = True

    # Act
    result = sut.update("abc123", {"name": "Test"})

    # Assert
    sut.dao.update.assert_called_once_with(id="abc123", update_data={"$set": {"name": "Test"}})
    assert result is True


# ---------------------------------------------------------------------------
# TC8 EXTRA, update() raises exception from DAO
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_update_database_error_raises_exception(sut):
    """When the DAO raises an exception during update, it should propogate."""
    # Arrange
    sut.dao.update.side_effect = Exception("Database error")

    # Act
    with pytest.raises(Exception, match="Database update error"):
        sut.update("abc123", {"name": "Test"})

    sut.dao.update.assert_called_once_with(id="abc123", update_data={"$set": {"name": "Test"}})
