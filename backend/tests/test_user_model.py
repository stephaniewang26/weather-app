import pytest
import sqlite3
import os
from models.User_Modelcopy import User  # Corrected import
from sample_user_data import SAMPLE_USERS

# --- Test Fixture ---
@pytest.fixture(scope="function")
def temp_database():
    """Fixture to create a temporary SQLite database for testing."""
    db_path = "test_user_model.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture(scope="function")
def user_model(temp_database):
    """Fixture to create a User model instance with a temporary database."""
    user = User(db_name=temp_database, table_name="users")
    user.initialize_table()
    return user

@pytest.fixture
def valid_user_data():
    """Fixture to provide valid user data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "preference_temperature": "neutral",
        "google_oauth_token": "test_token_123",
    }

@pytest.fixture
def another_valid_user_data():
    """Fixture to provide valid user data for testing."""
    return {
        "name": "Test User 2",
        "email": "test2@example.com",
        "preference_temperature": "neutral",
        "google_oauth_token": "test2_token_123",
    }

@pytest.fixture
def invalid_user_data_duplicate_email():
    """Fixture to provide valid user data for testing."""
    return {
        "name": "Test User 3",
        "email": "test@example.com",
        "preference_temperature": "neutral",
        "google_oauth_token": "test3_token_123",
    }

# --- Test Functions ---
def test_initialize_table_creates_table(temp_database):
    """Test that initialize_table creates the table successfully."""
    user = User(db_name=temp_database, table_name="users")
    user.initialize_table()

    # Verify the table exists
    conn = sqlite3.connect(temp_database)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table = cursor.fetchone()
    conn.close()

    assert table is not None, "Table 'users' was not created."

def test_initialize_table_schema(temp_database):
    """Test that the table schema matches the expected schema."""
    user = User(db_name=temp_database, table_name="users")
    user.initialize_table()

    # Verify the table schema
    conn = sqlite3.connect(temp_database)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users);")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    conn.close()

    expected_columns = {
        "id": "INTEGER",
        "name": "TEXT",
        "email": "TEXT",
        "preference_temperature": "TEXT",
        "google_oauth_token": "TEXT",
    }
    assert columns == expected_columns, f"Schema mismatch. Expected: {expected_columns}, Found: {columns}"

def test_initialize_table_idempotency(temp_database):
    """Test that calling initialize_table multiple times does not cause errors."""
    user = User(db_name=temp_database, table_name="users")
    user.initialize_table()
    try:
        user.initialize_table()  # Call it again
    except Exception as e:
        pytest.fail(f"initialize_table raised an exception on second call: {e}")

def test_initialize_table_creates_index(temp_database):
    """Test that the index on the email column is created."""
    user = User(db_name=temp_database, table_name="users")
    user.initialize_table()

    # Verify the index exists
    conn = sqlite3.connect(temp_database)
    cursor = conn.cursor()
    cursor.execute("PRAGMA index_list(users);")
    indexes = [row[1] for row in cursor.fetchall()]
    conn.close()

    assert any("email" in index for index in indexes), "Index on 'email' was not created."

def test_create_user_success(user_model, valid_user_data):
    """Test that a user can be created successfully with valid data."""
    result = user_model.create(valid_user_data)
    assert result["status"] == "success"
    assert "data" in result
    assert isinstance(result["data"], dict)
    assert "id" in result["data"]
    assert result["data"]["name"] == valid_user_data["name"]
    assert result["data"]["email"] == valid_user_data["email"]
    assert result["data"]["preference_temperature"] == valid_user_data["preference_temperature"]
    assert result["data"]["google_oauth_token"] == valid_user_data["google_oauth_token"]

    # Verify the user is in the database
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {user_model.table_name} WHERE id = ?;", (result["data"]["id"],))
    user_from_db = cursor.fetchone()
    conn.close()

    assert user_from_db is not None
    assert user_from_db[1] == valid_user_data["name"]
    assert user_from_db[2] == valid_user_data["email"]
    assert user_from_db[3] == valid_user_data["preference_temperature"]
    assert user_from_db[4] == valid_user_data["google_oauth_token"]

def test_create_multiple_users_unique_ids(user_model, valid_user_data, another_valid_user_data):
    """Test that creating multiple users results in unique IDs."""
    user1_result = user_model.create(valid_user_data)
    user2_result = user_model.create(another_valid_user_data)

    assert user1_result["status"] == "success"
    assert user2_result["status"] == "success"
    assert user1_result["data"]["id"] != user2_result["data"]["id"]

    # Verify both users are in the database
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {user_model.table_name};")
    all_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert user1_result["data"]["id"] in all_ids
    assert user2_result["data"]["id"] in all_ids
    assert len(all_ids) == 2

def test_create_user_duplicate_email(user_model, invalid_user_data_duplicate_email):
    """Test that creating a user with a duplicate email fails."""
    user_model.create({
        "name": "Test User",
        "email": "test@example.com",
        "preference_temperature": "neutral",
        "google_oauth_token": "test_token_123",
    })
    result = user_model.create(invalid_user_data_duplicate_email)
    assert result["status"] == "error"
    assert "data" in result
    assert isinstance(result["data"], sqlite3.IntegrityError)

    # Verify that only one user with the original email exists
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {user_model.table_name} WHERE email = ?;", (invalid_user_data_duplicate_email["email"],))
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 1

def test_create_user_optional_google_oauth_token_none(user_model, valid_user_data):
    """Test that google_oauth_token can be None."""
    valid_user_data["google_oauth_token"] = None
    result = user_model.create(valid_user_data)
    assert result["status"] == "success"
    assert "data" in result
    assert result["data"]["google_oauth_token"] is None

    # Verify None value in the database
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT google_oauth_token FROM {user_model.table_name} WHERE id = ?;", (result["data"]["id"],))
    token = cursor.fetchone()[0]
    conn.close()
    assert token is None

def test_create_user_generates_valid_id(user_model, valid_user_data):
    """Test that the generated ID is within the safe JavaScript integer range."""
    result = user_model.create(valid_user_data)
    assert result["status"] == "success"
    assert 0 <= result["data"]["id"] <= user_model.max_safe_id

# --- Tests for exists() ---
def test_exists_by_email_true(user_model):
    """Test exists() returns True if a user with the given email exists."""
    user_model.create(SAMPLE_USERS[0])
    result = user_model.exists(email=SAMPLE_USERS[0]["email"])
    assert result["status"] == "success"
    assert result["data"] is True

def test_exists_by_email_false(user_model):
    """Test exists() returns False if no user with the given email exists."""
    result = user_model.exists(email="nonexistent@example.com")
    assert result["status"] == "success"
    assert result["data"] is False

def test_exists_by_id_true(user_model):
    """Test exists() returns True if a user with the given ID exists."""
    created_user = user_model.create(SAMPLE_USERS[1])
    user_id = created_user["data"]["id"]
    result = user_model.exists(id=user_id)
    assert result["status"] == "success"
    assert result["data"] is True

def test_exists_by_id_false(user_model):
    """Test exists() returns False if no user with the given ID exists."""
    result = user_model.exists(id=999999)  # An ID that is unlikely to exist
    assert result["status"] == "success"
    assert result["data"] is False

def test_exists_with_no_parameters(user_model):
    """Test exists() returns False if no email or id is provided."""
    result = user_model.exists()
    assert result["status"] == "success"
    assert result["data"] is False

# --- Tests for get() ---
def test_get_by_email_success(user_model):
    """Test get() returns the user data if a user with the given email exists."""
    created_user = user_model.create(SAMPLE_USERS[2])
    result = user_model.get(email=SAMPLE_USERS[2]["email"])
    assert result["status"] == "success"
    assert "data" in result
    assert result["data"] == created_user["data"]  # Compare the entire user data dictionary

def test_get_by_email_user_not_found(user_model):
    """Test get() returns an error if no user with the given email exists."""
    result = user_model.get(email="nonexistent@example.com")
    assert result["status"] == "error"
    assert "data" in result
    assert result["data"] == "User does not exist!"

def test_get_by_id_success(user_model):
    """Test get() returns the user data if a user with the given ID exists."""
    created_user = user_model.create(SAMPLE_USERS[3])
    user_id = created_user["data"]["id"]
    result = user_model.get(id=user_id)
    assert result["status"] == "success"
    assert "data" in result
    assert result["data"] == created_user["data"]

def test_get_by_id_user_not_found(user_model):
    """Test get() returns an error if no user with the given ID exists."""
    result = user_model.get(id=999999)  # An ID that is unlikely to exist
    assert result["status"] == "error"
    assert "data" in result
    assert result["data"] == "User does not exist!"

def test_get_with_no_parameters(user_model):
    """Test get() returns an error if no email or id is provided."""
    result = user_model.get()
    assert result["status"] == "error"
    assert "data" in result
    assert result["data"] == "No email or id entered!"

# --- Comprehensive Tests using SAMPLE_USERS ---
def test_create_multiple_users_from_sample(user_model):
    """Test creating multiple users from SAMPLE_USERS data."""
    created_users = []
    for user_data in SAMPLE_USERS:
        result = user_model.create(user_data)
        assert result["status"] == "success"
        assert "data" in result
        created_users.append(result["data"])

    assert len(created_users) == len(SAMPLE_USERS)
    # Verify unique emails and ids
    emails = [user["email"] for user in created_users]
    ids = [user["id"] for user in created_users]
    assert len(emails) == len(set(emails))
    assert len(ids) == len(set(ids))

    # Verify data integrity by checking if data in db matches
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    for created_user in created_users:
        cursor.execute(f"SELECT * FROM {user_model.table_name} WHERE id = ?;", (created_user["id"],))
        user_from_db = cursor.fetchone()
        assert user_from_db is not None
        # convert user_from_db to dict and compare
        user_from_db_dict = {
            "id": user_from_db[0],
            "name": user_from_db[1],
            "email": user_from_db[2],
            "preference_temperature": user_from_db[3],
            "google_oauth_token": user_from_db[4],
        }
        assert user_from_db_dict == created_user

    conn.close()

def test_exists_with_sample_data(user_model):
    """Test exists() function with data from SAMPLE_USERS."""
    for user_data in SAMPLE_USERS:
        user_model.create(user_data)

    for user_data in SAMPLE_USERS:
        assert user_model.exists(email=user_data["email"])["data"] is True
        # get user id and test exists by id
        user_id_from_db = user_model.get(email=user_data["email"])["data"]["id"]
        assert user_model.exists(id=user_id_from_db)["data"] is True

    assert user_model.exists(email="nonexistent@example.com")["data"] is False
    assert user_model.exists(id=999999)["data"] is False

def test_get_with_sample_data(user_model):
    """Test get() function with data from SAMPLE_USERS."""
    for user_data in SAMPLE_USERS:
        user_model.create(user_data)

    for user_data in SAMPLE_USERS:
        user_by_email = user_model.get(email=user_data["email"])["data"]
        user_id_from_db = user_model.get(email=user_data["email"])["data"]["id"]
        user_by_id = user_model.get(id=user_id_from_db)["data"]

        #get rid of the id from the user_by_email and user_by_id
        del user_by_email['id']
        del user_by_id['id']

        # compare the dictionaries
        assert user_by_email == user_data
        assert user_by_id == user_data

    assert user_model.get(email="nonexistent@example.com")["data"] == "User does not exist!"
    assert user_model.get(id=999999)["data"] == "User does not exist!"

# --- Tests for get_all() ---
def test_get_all_empty_table(user_model):
    """Test get_all() returns an empty list when the table is empty."""
    result = user_model.get_all()
    assert result["status"] == "success"
    assert result["data"] == []

def test_get_all_single_user(user_model, valid_user_data):
    """Test get_all() returns a list containing one user when there is only one user in the table."""
    user_model.create(valid_user_data)
    result = user_model.get_all()
    assert result["status"] == "success"
    assert isinstance(result["data"], list)
    assert len(result["data"]) == 1
    # Ensure the returned user data matches the created user data
    expected_user = {
        "id": result["data"][0]["id"],  # Use the generated ID
        "name": valid_user_data["name"],
        "email": valid_user_data["email"],
        "preference_temperature": valid_user_data["preference_temperature"],
        "google_oauth_token": valid_user_data["google_oauth_token"],
    }
    assert result["data"][0] == expected_user

def test_get_all_multiple_users(user_model):
    """Test get_all() returns a list containing all users when there are multiple users in the table."""
    for user_data in SAMPLE_USERS:
        user_model.create(user_data)
    result = user_model.get_all()
    assert result["status"] == "success"
    assert isinstance(result["data"], list)
    assert len(result["data"]) == len(SAMPLE_USERS)

    # Verify that the returned data matches the SAMPLE_USERS data, order doesn't matter
    expected_users = []
    for user_dict in SAMPLE_USERS:
        expected_user = user_dict.copy()
        # find the user in result
        found = False
        for res_user in result["data"]:
            if res_user["email"] == expected_user["email"]:
                expected_user["id"] = res_user["id"] # set the correct id
                expected_users.append(expected_user)
                found = True
                break
        assert found == True
    assert len(expected_users) == len(SAMPLE_USERS)
    assert set(tuple(sorted(d.items())) for d in result["data"]) == set(tuple(sorted(d.items())) for d in expected_users)

def test_get_all_user_data_integrity(user_model):
    """Test that get_all() returns the correct user data for all users."""
    # Create users from SAMPLE_USERS
    for user_data in SAMPLE_USERS:
        user_model.create(user_data)

    result = user_model.get_all()

    # Fetch user data directly from the database for comparison
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {user_model.table_name};")
    users_from_db = cursor.fetchall()
    conn.close()

    # Convert database results to a list of dictionaries
    expected_users_from_db = [
        {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "preference_temperature": user[3],
            "google_oauth_token": user[4],
        }
        for user in users_from_db
    ]
    assert set(tuple(sorted(d.items())) for d in result["data"]) == set(tuple(sorted(d.items())) for d in expected_users_from_db)