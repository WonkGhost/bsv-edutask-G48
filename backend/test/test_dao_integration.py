import pytest
import pymongo
from unittest.mock import patch

from bson import ObjectId

from src.util.dao import DAO

TEST_COLLECTION = "test_integration_users"

USER_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["firstName", "lastName", "email"],
        "properties": {
            "firstName": {
                "bsonType": "string",
                "description": "the first name of the user must be determined"
            },
            "lastName": {
                "bsonType": "string",
                "description": "the last name of the user must be determined"
            },
            "email": {
                "bsonType": "string",
                "description": "the email of the user must be determined",
                "uniqueItems": True
            },
            "tasks": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                }
            }
        }
    }
}

# ---------------------------------------------------------------------------
# Fixture: a DAO to a test collection with a validator
# ---------------------------------------------------------------------------

@ pytest.fixture
def dao():

    with patch('src.util.dao.getValidator', return_value=USER_VALIDATOR):
        d = DAO(TEST_COLLECTION)
        
    d.collection.create_index("email", unique=True)

    yield d

    d.collection.drop()
    
# ---------------------------------------------------------------------------
# TC1 – Valid document: all required fields are present.
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_create_valid_document_returns_document_with_id(dao):

    # Arrange
    data = {"firstName": "John", "lastName": "Doe", "email": "test@test.com"}
    
    # Act
    result = dao.create(data)

    # Assert
    assert result is not None
    assert "_id" in result
    assert result["firstName"] == "John"
    assert result["lastName"] == "Doe" 
    assert result["email"] == "test@test.com"

# ---------------------------------------------------------------------------
# TC2 – Missing required field: 'firstName'
# ---------------------------------------------------------------------------

@ pytest.mark.integration
def test_create_missing_firstName_raises_error(dao):

    # Arrange
    data = {"lastName": "Doe", "email": "test@test.com"}

    # Act & Assert
    with pytest.raises(pymongo.errors.WriteError):
        dao.create(data)

# ---------------------------------------------------------------------------
# TC3 – Missing required field: 'lastName'
# ---------------------------------------------------------------------------

@ pytest.mark.integration
def test_create_missing_lastName_raises_error(dao):
    # Arrange
    data = {"firstName": "John", "email": "test@test.com"}

    # Act & Assert
    with pytest.raises(pymongo.errors.WriteError):
        dao.create(data)

# ---------------------------------------------------------------------------
# TC4 – Missing required field: 'email'
# ---------------------------------------------------------------------------

@ pytest.mark.integration
def test_create_missing_email_raises_error(dao):
    # Arrange
    data = {"firstName": "John", "lastName": "Doe"}

    # Act & Assert
    with pytest.raises(pymongo.errors.WriteError):
        dao.create(data)

# ---------------------------------------------------------------------------
# TC5 - Wrong data type: 'firstName' is not a string
# ---------------------------------------------------------------------------

@ pytest.mark.integration
def test_create_wrong_type_firstName_raises_error(dao):
    # Arrange
    data = {"firstName": 123, "lastName": "Doe", "email": "test@test.com"}

    # Act & Assert
    with pytest.raises(pymongo.errors.WriteError):
        dao.create(data)

# ---------------------------------------------------------------------------
# TC6 - Invalid email: 'email' is not a string
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_create_wrong_type_email_raises_error(dao):
    # Arrange
    data = {"firstName": "Alice", "lastName": "Smith", "email": True}

    # Act & Assert
    with pytest.raises(pymongo.errors.WriteError):
        dao.create(data)

# ---------------------------------------------------------------------------
# TC7 - Unique email: two documents with the same email
# ---------------------------------------------------------------------------

@ pytest.mark.integration
def test_create_duplicate_email_raises_error(dao):
    # Arrange
    data1 = {"firstName": "John", "lastName": "Doe", "email": "test@test.com"}
    data2 = {"firstName": "Jane", "lastName": "Smith", "email": "test@test.com"}

    # Act
    dao.create(data1)

    # Assert
    with pytest.raises(Exception):
        dao.create(data2)

#---------------------------------------------------------------------------
# TC8 - Valid tasks: 'tasks' is an array of ObjectIds
#---------------------------------------------------------------------------

@ pytest.mark.integration
def test_create_valid_tasks(dao):

    # Arrange
    data = {"firstName": "John", "lastName": "Doe", "email": "test@test.com", "tasks": [ObjectId("60f7b1b2f1d2b3a4e567890a")]}

    # Act
    result = dao.create(data)

    # Assert
    assert result["tasks"][0]["$oid"] == "60f7b1b2f1d2b3a4e567890a"
    
#---------------------------------------------------------------------------
# TC9 - Invalid tasks: 'tasks' is not an array of ObjectIds
#---------------------------------------------------------------------------

@ pytest.mark.integration
def test_create_invalid_tasks_raises_error(dao):

    # Arrange
    data = {"firstName": "John", "lastName": "Doe", "email": "test@test.com", "tasks": "tasks"}

    # Act & Assert
    with pytest.raises(pymongo.errors.WriteError):
        dao.create(data)