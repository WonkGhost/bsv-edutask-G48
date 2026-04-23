import pytest
import pymongo
from unittest.mock import patch

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


@pytest.fixture
def test_db():
    # Create a test database connection
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    test_db = client["test_db"]
    
    # Ensure the test database is clean before each test
    test_db.drop_collection("test_collection")
    
    yield test_db
    
    # Clean up after tests
    client.drop_database("test_db")
    client.close

@ pytest.fixture
def dao():

    with patch('src.util.dao.getValidator', return_value=USER_VALIDATOR):
        d = DAO("test_users")
        
    d.collection.create_index("email", unique=True)

    yield d

    d.collection.drop()


    
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