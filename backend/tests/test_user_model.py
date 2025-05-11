import pytest
import sqlite3
import os
from models.User_Model import User  # Corrected import
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

# --- Tests for update() ---
def test_update_user_success(user_model, valid_user_data):
    """Test that a user can be updated successfully with valid data."""
    # 1. Create a user first
    create_result = user_model.create(valid_user_data)
    user_id = create_result["data"]["id"]

    # 2. Modify the user data
    updated_user_data = {
        "id": user_id,
        "name": "Updated User Name",
        "email": "updated@example.com",
    }

    # 3. Update the user
    update_result = user_model.update(updated_user_data)
    assert update_result["status"] == "success"
    assert "data" in update_result
    assert isinstance(update_result["data"], dict)
    assert update_result["data"]["id"] == user_id
    assert update_result["data"]["name"] == "Updated User Name"
    assert update_result["data"]["email"] == "updated@example.com"
    #check other fields were not changed
    assert update_result["data"]["preference_temperature"] == valid_user_data["preference_temperature"]
    assert update_result["data"]["google_oauth_token"] == valid_user_data["google_oauth_token"]

    # 4. Verify the update in the database
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {user_model.table_name} WHERE id = ?;", (user_id,))
    updated_user_from_db = cursor.fetchone()
    conn.close()

    assert updated_user_from_db is not None
    assert updated_user_from_db[1] == "Updated User Name"
    assert updated_user_from_db[2] == "updated@example.com"
    assert updated_user_from_db[3] == valid_user_data["preference_temperature"]
    assert updated_user_from_db[4] == valid_user_data["google_oauth_token"]


def test_update_user_invalid_id(user_model, valid_user_data):
    """Test that updating a user with an invalid ID returns an error."""
    invalid_user_data = {
        "id": 999999,  # An ID that is unlikely to exist
        "name": "Updated User Name",
        "email": "updated@example.com",
    }
    result = user_model.update(invalid_user_data)
    assert result["status"] == "error"
    assert "data" in result
    assert result["data"] == "Id does not exist!"

def test_update_user_duplicate_email(user_model, valid_user_data, another_valid_user_data):
    """Test that updating a user with a duplicate email fails."""
    # 1. Create two users
    user1_result = user_model.create(valid_user_data)
    user2_result = user_model.create(another_valid_user_data)
    user1_id = user1_result["data"]["id"]
    user2_id = user2_result["data"]["id"]

    # 2. Attempt to update user1's email to user2's email
    invalid_update_data = {
        "id": user1_id,
        "name": "Updated User Name",
        "email": another_valid_user_data["email"],  # Duplicate email
    }
    result = user_model.update(invalid_update_data)
    assert result["status"] == "error"
    assert result["data"] == "Email address already exists!"

    # 3. Verify that user1's email was not changed in the database
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT email FROM {user_model.table_name} WHERE id = ?;", (user1_id,))
    user1_email_from_db = cursor.fetchone()[0]
    conn.close()
    assert user1_email_from_db == valid_user_data["email"]  # Original email


def test_update_user_invalid_email_format(user_model, valid_user_data):
    """Test that updating a user with an invalid email format."""
    # 1. Create a user.
    created_user = user_model.create(valid_user_data)
    user_id = created_user["data"]["id"]
    invalid_email_formats = [
        "invalid_email",
        "invalid@email",
        "invalid.email",
        "invalid email@test.com",
    ]

    for invalid_email in invalid_email_formats:
        # 2. Attempt to update the user's email with an invalid format
        invalid_update_data = {
            "id": user_id,
            "name": "Updated Name",
            "email": invalid_email,
        }
        result = user_model.update(invalid_update_data)
        assert result["status"] == "error"
        assert "data" in result
        assert "Email address should contain @ character." in result["data"] or \
               "Email address should contain . character." in result["data"] or \
               "Email address should not contain any spaces." in result["data"]

        # 3. Verify that the email was not changed
        conn = sqlite3.connect(user_model.db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT email FROM {user_model.table_name} WHERE id = ?;", (user_id,))
        email_from_db = cursor.fetchone()[0]
        conn.close()
        assert email_from_db == valid_user_data["email"]  # Original email

def test_update_user_valid_email_format(user_model, valid_user_data):
    """Test that updating a user with a valid email format."""
    # 1. Create a user.
    created_user = user_model.create(valid_user_data)
    user_id = created_user["data"]["id"]
    valid_email_format = "valid.email@test.com"
    # 2. Attempt to update the user's email with a valid format
    valid_update_data = {
        "id": user_id,
        "name": "Updated Name",
        "email": valid_email_format,
    }
    result = user_model.update(valid_update_data)
    assert result["status"] == "success"
    assert "data" in result
    assert result["data"]["email"] == valid_email_format

    # 3. Verify that the email was changed
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT email FROM {user_model.table_name} WHERE id = ?;", (user_id,))
    email_from_db = cursor.fetchone()[0]
    conn.close()
    assert email_from_db == valid_email_format

def test_update_user_name_change(user_model, valid_user_data):
    """Test that updating a user's name changes only the name."""
    # 1. Create a user
    create_result = user_model.create(valid_user_data)
    user_id = create_result["data"]["id"]
    updated_name = "New Name"

    # 2. Update only the name
    updated_data = {"id": user_id, "name": updated_name, "email": valid_user_data["email"]}  # Include original email
    result = user_model.update(updated_data)

    # 3. Assert success and check the updated name
    assert result["status"] == "success"
    assert result["data"]["name"] == updated_name

    # 4. Verify in the database
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM {user_model.table_name} WHERE id = ?;", (user_id,))
    name_from_db = cursor.fetchone()[0]
    conn.close()
    assert name_from_db == updated_name

def test_update_user_email_change(user_model, valid_user_data):
    """Test that updating a user's email changes only the email."""
    # 1. Create a user
    create_result = user_model.create(valid_user_data)
    user_id = create_result["data"]["id"]
    updated_email = "new_email@test.com"

    # 2. Update only the email
    updated_data = {"id": user_id, "email": updated_email, "name": valid_user_data["name"]}  # Include original name
    result = user_model.update(updated_data)

    # 3. Assert success and check the updated email
    assert result["status"] == "success"
    assert result["data"]["email"] == updated_email

    # 4. Verify in the database
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT email FROM {user_model.table_name} WHERE id = ?;", (user_id,))
    email_from_db = cursor.fetchone()[0]
    conn.close()
    assert email_from_db == updated_email

# --- Tests for remove() ---
def test_remove_user_success(user_model, valid_user_data):
    """Test that a user can be removed successfully by email."""
    # 1. Create a user
    create_result = user_model.create(valid_user_data)
    user_email = valid_user_data["email"]

    # 2. Remove the user
    remove_result = user_model.remove(user_email)
    assert remove_result["status"] == "success"
    assert "data" in remove_result
    assert remove_result["data"]["email"] == user_email

    # 3. Verify that the user is removed from the database
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {user_model.table_name} WHERE email = ?;", (user_email,))
    user_from_db = cursor.fetchone()
    conn.close()
    assert user_from_db is None, "User was not removed from the database"


def test_remove_user_not_exists(user_model):
    """Test that removing a non-existent user returns an error."""
    nonexistent_email = "nonexistent@example.com"
    result = user_model.remove(nonexistent_email)
    assert result["status"] == "error"
    assert "data" in result
    assert result["data"] == "User does not exist!", "Incorrect error message"


def test_remove_only_removes_specified_user(user_model):
    """Test that remove() only removes the specified user, leaving others intact."""
    # 1. Create multiple users
    for user_data in SAMPLE_USERS:
        user_model.create(user_data)
    email_to_remove = SAMPLE_USERS[2]["email"]  # Choose an email to remove

    # 2. Remove one user
    user_model.remove(email_to_remove)

    # 3. Verify that the correct user is removed and others remain
    conn = sqlite3.connect(user_model.db_name)
    cursor = conn.cursor()

    # Check if the removed user is still present
    cursor.execute(f"SELECT * FROM {user_model.table_name} WHERE email = ?;", (email_to_remove,))
    removed_user_from_db = cursor.fetchone()
    assert removed_user_from_db is None, "Removed user is still in the database"

    # Check that other users are still present
    for user_data in SAMPLE_USERS:
        if user_data["email"] != email_to_remove:
            cursor.execute(f"SELECT * FROM {user_model.table_name} WHERE email = ?;", (user_data["email"],))
            user_from_db = cursor.fetchone()
            assert user_from_db is not None, f"User with email {user_data['email']} was incorrectly removed"
    conn.close()