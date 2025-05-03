# tests/test_user_model.py
import pytest
import sqlite3
import os
import sys

# --- Path Setup ---
# Add the project root directory to the Python path.
# This allows importing modules from sibling directories like 'models'.
# This assumes the 'tests' directory is directly inside the project root.
# os.path.abspath(__file__) gives the absolute path of this test file.
# os.path.dirname(...) gets the directory containing this file ('tests').
# os.path.dirname(os.path.dirname(...)) gets the parent directory (project root).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# --- Imports ---
# Now we can import the User class and its constants from the models directory
from models.User_Model import User, DB_PATH, DB_DIR
# Import the sample data from the sibling file within the tests directory
from tests.sample_user_data import SAMPLE_USERS

# --- Test Fixture ---
@pytest.fixture(scope="function", autouse=True)
def setup_teardown_database():
    """
    Pytest fixture executed automatically before each test function (`autouse=True`).
    Sets up a clean database state for testing and tears it down afterwards.

    Scope: 'function' ensures this runs independently for every test function,
           providing isolation between tests.

    Steps:
    1. Ensure the 'data' directory exists using the path from User_Model.
    2. Delete the database file (`database.db`) if it exists to ensure a clean slate.
    3. Call User.initialize_table() to create the 'users' table schema.
    4. Populate the 'users' table with fresh data from SAMPLE_USERS.
    5. Yield control to the test function execution.
    6. (Teardown - Optional) Clean up by deleting the database file after the test runs.
       Leaving it can sometimes be useful for debugging failed tests.
    """
    # --- Setup Phase ---
    try:
        # 1. Ensure the data directory exists
        os.makedirs(DB_DIR, exist_ok=True)

        # 2. Delete the database file if it exists for a clean start
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            # print(f"Removed existing database: {DB_PATH}") # Optional debug print

        # 3. Initialize the table schema
        User.initialize_table()
        # print(f"Initialized table in database: {DB_PATH}") # Optional debug print

        # 4. Populate with sample data
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for user_data in SAMPLE_USERS:
            cursor.execute(
                "INSERT INTO users (name, email, preference_temperature, google_oauth_token) VALUES (?, ?, ?, ?)",
                (user_data['name'], user_data['email'], user_data['preference_temperature'], user_data.get('google_oauth_token'))
            )
        conn.commit()
        conn.close()
        # print(f"Populated database with {len(SAMPLE_USERS)} users.") # Optional debug print

    except Exception as e:
        # If any part of the setup fails, report the error and fail the test suite run for this test.
        pytest.fail(f"Database setup failed in fixture: {e}")

    # --- Yield to Test ---
    # The test function runs here.
    yield

    # --- Teardown Phase ---
    # Optional: Clean up the database file after the test. Comment out if you want to inspect the DB after failures.
    # try:
    #     if os.path.exists(DB_PATH):
    #         os.remove(DB_PATH)
    #         # print(f"Cleaned up database: {DB_PATH}") # Optional debug print
    # except Exception as e:
    #     print(f"Warning: Failed to remove database during teardown: {e}")


# --- Test Functions ---

# Test __init__ and basic validation
def test_user_init_valid():
    """Tests successful initialization of a User object with valid data."""
    user = User(name="Valid User", email="valid@test.com", preference_temperature="gets_cold_easily", google_oauth_token="valid_token")
    assert user.name == "Valid User"
    assert user.email == "valid@test.com"
    assert user.preference_temperature == "gets_cold_easily"
    assert user.google_oauth_token == "valid_token"
    assert user.id is None # ID should be None on initial creation

def test_user_init_default_preference():
    """Tests that the default temperature preference is 'neutral'."""
    user = User(name="Default Pref", email="default@test.com")
    assert user.preference_temperature == "neutral"

def test_user_init_invalid_preference_raises_error():
    """Tests that initializing a User with an invalid preference raises ValueError."""
    with pytest.raises(ValueError, match="preference_temperature must be one of"):
        User(name="Invalid Pref", email="invalid@pref.com", preference_temperature="luke_warm")

# Test initialize_table (primarily idempotency, as fixture calls it first)
def test_initialize_table_idempotency():
    """
    Tests that calling initialize_table multiple times doesn't cause errors
    and the table structure remains correct. Relies on the fixture having run it once.
    """
    try:
        # Call initialize_table again after the fixture has already done so
        User.initialize_table()

        # Verify table still exists and has correct columns using PRAGMA
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        assert cursor.fetchone() is not None, "Table 'users' should still exist after second initialization."

        cursor.execute("PRAGMA table_info(users);")
        columns = {row[1] for row in cursor.fetchall()} # Extract column names into a set
        expected_columns = {'id', 'name', 'email', 'preference_temperature', 'google_oauth_token'}
        assert columns == expected_columns, "Table columns should remain correct after second initialization."

        # Verify index exists
        cursor.execute("PRAGMA index_list(users);")
        indexes = [row[1] for row in cursor.fetchall()]
        assert 'idx_user_email' in indexes, "Index 'idx_user_email' should exist."

        conn.close()
    except Exception as e:
        pytest.fail(f"Error during idempotency test for initialize_table: {e}")

# Test save() method
def test_save_new_user_success():
    """Tests saving a completely new, valid user successfully."""
    new_user = User(
        name="Fiona Gallagher",
        email="fiona@example.com", # Unique email
        preference_temperature="neutral",
        google_oauth_token="token_fiona_abc"
    )
    try:
        new_user.save() # Call the method under test
    except Exception as e:
        pytest.fail(f"User.save() raised an unexpected exception: {e}")

    # --- Assertions after save ---
    assert new_user.id is not None, "User ID should be set by the database after saving."
    assert isinstance(new_user.id, int), "User ID should be an integer."
    assert new_user.id > len(SAMPLE_USERS), "New ID should be greater than existing sample IDs."

    # --- Verify by fetching the user back from the DB ---
    fetched_user = User.get_by_id(new_user.id)
    assert fetched_user is not None, "Failed to fetch the newly saved user by ID."
    # Use the __eq__ method defined in User class for a comprehensive comparison
    assert fetched_user == new_user, "Fetched user data does not match the original saved user data."
    assert fetched_user.name == "Fiona Gallagher" # Spot check attribute

def test_save_user_duplicate_email_raises_error():
    """Tests that saving a user with an email that already exists raises ValueError."""
    existing_user_email = SAMPLE_USERS[0]['email'] # 'alice@example.com'
    user_with_duplicate_email = User(name="Another Alice", email=existing_user_email)

    # Expecting a ValueError due to the UNIQUE constraint violation, wrapped by our save method
    with pytest.raises(ValueError, match=f"Email '{existing_user_email}' already exists"):
        user_with_duplicate_email.save()

    # Double-check: ensure the original user wasn't affected
    original_user = User.get_by_email(existing_user_email)
    assert original_user is not None
    assert original_user.name == SAMPLE_USERS[0]['name'], "Original user data should not have been altered."

def test_save_user_with_id_raises_error():
    """Tests that calling save() on a User instance that already has an ID raises ValueError."""
    # Fetch an existing user (which will have an ID assigned)
    user_to_save_again = User.get_by_email(SAMPLE_USERS[1]['email']) # Get Bob
    assert user_to_save_again is not None and user_to_save_again.id is not None, "Fixture setup failed or get_by_email failed."

    # Expecting a ValueError because save() is intended only for new records (ID is None)
    with pytest.raises(ValueError, match="already has an ID"):
        user_to_save_again.save()

# Test get_by_id() method
def test_get_by_id_existing_user():
    """Tests retrieving an existing user by their known ID."""
    # Assuming IDs are sequential starting from 1 based on SAMPLE_USERS insertion order
    expected_user_data = SAMPLE_USERS[0] # Alice
    user_id_to_find = 1 # Assuming Alice got ID 1

    fetched_user = User.get_by_id(user_id_to_find)

    assert fetched_user is not None, f"User with ID {user_id_to_find} should exist but was not found."
    # Verify all attributes match the expected sample data
    assert fetched_user.id == user_id_to_find
    assert fetched_user.name == expected_user_data['name']
    assert fetched_user.email == expected_user_data['email']
    assert fetched_user.preference_temperature == expected_user_data['preference_temperature']
    assert fetched_user.google_oauth_token == expected_user_data['google_oauth_token']

def test_get_by_id_non_existent_user():
    """Tests retrieving a user by an ID that does not exist in the database."""
    non_existent_id = 9999 # An ID guaranteed not to exist
    fetched_user = User.get_by_id(non_existent_id)
    assert fetched_user is None, f"User.get_by_id should return None for non-existent ID {non_existent_id}."

# Test get_by_email() method
def test_get_by_email_existing_user():
    """Tests retrieving an existing user by their unique email address."""
    expected_user_data = SAMPLE_USERS[2] # Charlie
    email_to_find = expected_user_data['email']

    fetched_user = User.get_by_email(email_to_find)

    assert fetched_user is not None, f"User with email '{email_to_find}' should exist but was not found."
    # Verify all attributes match
    assert fetched_user.email == email_to_find
    assert fetched_user.name == expected_user_data['name']
    assert fetched_user.preference_temperature == expected_user_data['preference_temperature']
    assert fetched_user.google_oauth_token == expected_user_data['google_oauth_token']
    # Check ID consistency (assuming sequential IDs)
    assert fetched_user.id == 3 # Assuming Charlie got ID 3

def test_get_by_email_non_existent_user():
    """Tests retrieving a user by an email address that does not exist."""
    non_existent_email = "nosuchuser@example.com"
    fetched_user = User.get_by_email(non_existent_email)
    assert fetched_user is None, f"User.get_by_email should return None for non-existent email '{non_existent_email}'."

# Test update() method
def test_update_user_details_success():
    """Tests successfully updating multiple attributes of an existing user."""
    user_to_update_id = 2 # Bob's assumed ID
    user_to_update = User.get_by_id(user_to_update_id)
    assert user_to_update is not None, f"Setup failed: Could not retrieve user ID {user_to_update_id} for update test."

    # Store original email to ensure it doesn't change unless intended
    original_email = user_to_update.email

    # Modify attributes on the fetched instance
    user_to_update.name = "Robert 'Bob' Builder"
    user_to_update.preference_temperature = "gets_cold_easily"
    user_to_update.google_oauth_token = "new_bob_token_xyz"

    # Call the update method
    update_successful = user_to_update.update()
    assert update_successful is True, "User.update() should return True on successful update."

    # --- Verify the changes by fetching the user again from the DB ---
    updated_user = User.get_by_id(user_to_update_id)
    assert updated_user is not None, f"Failed to fetch user ID {user_to_update_id} after update."
    assert updated_user.name == "Robert 'Bob' Builder"
    assert updated_user.email == original_email # Email should remain unchanged here
    assert updated_user.preference_temperature == "gets_cold_easily"
    assert updated_user.google_oauth_token == "new_bob_token_xyz"
    # The updated instance in memory should now equal the re-fetched instance
    assert updated_user == user_to_update

def test_update_user_changing_email_success():
    """Tests successfully updating an existing user's email address to a new, unique email."""
    user_to_update_id = 4 # Diana's assumed ID
    user_to_update = User.get_by_id(user_to_update_id)
    assert user_to_update is not None

    original_email = user_to_update.email
    new_email = "diana.prince@themyscira.com" # A new unique email

    user_to_update.email = new_email # Change email on the instance

    update_successful = user_to_update.update()
    assert update_successful is True, "User.update() should return True when changing to a valid new email."

    # --- Verification ---
    # Fetch by new email - should find the updated user
    updated_user = User.get_by_email(new_email)
    assert updated_user is not None
    assert updated_user.id == user_to_update_id
    assert updated_user.name == user_to_update.name # Other attributes remain

    # Fetch by old email - should NOT find the user
    assert User.get_by_email(original_email) is None, "User should no longer be found by the old email address."

def test_update_user_duplicate_email_fails():
    """Tests that updating a user's email to one that already exists for *another* user fails."""
    user_to_update_id = 2 # Bob's ID
    user_to_update = User.get_by_id(user_to_update_id)
    assert user_to_update is not None

    email_of_other_user = SAMPLE_USERS[0]['email'] # Alice's email
    original_bob_email = user_to_update.email

    # Attempt to change Bob's email to Alice's email
    user_to_update.email = email_of_other_user

    update_successful = user_to_update.update()
    # Expecting update to fail (return False) because of the UNIQUE constraint violation
    assert update_successful is False, "User.update() should return False when causing a duplicate email conflict."

    # --- Verification ---
    # Verify Bob's email hasn't actually changed in the database
    fetched_bob = User.get_by_id(user_to_update_id)
    assert fetched_bob is not None
    assert fetched_bob.email == original_bob_email, "Bob's email should not have changed in the DB after failed update."

    # Verify Alice still has her email
    fetched_alice = User.get_by_email(email_of_other_user)
    assert fetched_alice is not None
    assert fetched_alice.id == 1 # Alice's assumed ID

def test_update_user_with_invalid_preference_fails_at_db():
    """
    Tests if the DB CHECK constraint prevents updating to an invalid preference.
    Note: The __init__ prevents creating such an object directly, but this tests
    if bypassing init (e.g., direct attribute modification) would be caught by DB.
    This requires modifying the object *after* fetching.
    """
    user_to_update_id = 1 # Alice
    user_to_update = User.get_by_id(user_to_update_id)
    assert user_to_update is not None

    original_preference = user_to_update.preference_temperature

    # Directly modify the attribute, bypassing __init__ validation
    user_to_update.preference_temperature = "invalid_preference_value"

    # Expect the database CHECK constraint to raise an IntegrityError during UPDATE
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        # We need to directly execute SQL or bypass the model's update logic
        # if the model's update itself doesn't re-validate.
        # Let's assume the model's update() passes the value directly.
        # If update() returns False without raising, adjust the test.
        # For now, assume update() might raise the IntegrityError if not caught earlier.
        # If update() catches it and returns False, change to assert update_successful is False.
        conn = user_to_update._get_connection() # Use internal method for direct access
        cursor = conn.cursor()
        try:
             cursor.execute(
                """
                UPDATE users SET preference_temperature = ? WHERE id = ?
                """,
                (user_to_update.preference_temperature, user_to_update.id)
            )
        finally:
            conn.close() # Ensure connection is closed even on error


    # Verify the preference was not actually changed in the DB
    fetched_user = User.get_by_id(user_to_update_id)
    assert fetched_user is not None
    assert fetched_user.preference_temperature == original_preference


def test_update_non_existent_user_instance_fails():
    """Tests calling update() on a User instance that has no ID (was never saved/fetched)."""
    unsaved_user = User(name="Ghost User", email="ghost@example.com")
    assert unsaved_user.id is None # Precondition: User has no ID

    update_successful = unsaved_user.update()
    # The method should check for self.id is None and return False
    assert update_successful is False, "User.update() should return False for a user instance without an ID."

def test_update_non_existent_user_id_fails():
    """Tests calling update() on a User instance with an ID that doesn't exist in the DB."""
    non_existent_id = 9998
    # Create a user instance with an ID that is guaranteed not to exist
    user_with_bad_id = User(id=non_existent_id, name="Fake User", email="fake@example.com")

    update_successful = user_with_bad_id.update()
    # The SQL UPDATE command will affect 0 rows if the WHERE id=? clause doesn't match.
    # The update() method should return False based on cursor.rowcount.
    assert update_successful is False, "User.update() should return False if the user ID does not exist in the database."

# Test delete_by_id() method
def test_delete_by_id_existing_user_success():
    """Tests successfully deleting an existing user by their ID."""
    user_id_to_delete = 3 # Charlie's assumed ID

    # --- Pre-check ---
    assert User.get_by_id(user_id_to_delete) is not None, f"Setup failed: User ID {user_id_to_delete} not found before deletion test."
    initial_count = len(User.get_all())

    # --- Perform Deletion ---
    delete_successful = User.delete_by_id(user_id_to_delete)
    assert delete_successful is True, "User.delete_by_id() should return True for successful deletion."

    # --- Verification ---
    # Verify the user is actually gone by trying to fetch them
    deleted_user = User.get_by_id(user_id_to_delete)
    assert deleted_user is None, f"User ID {user_id_to_delete} should not be found after deletion."

    # Verify the total count of users has decreased by one
    final_count = len(User.get_all())
    assert final_count == initial_count - 1, "Total user count should decrease by one after deletion."

    # Verify other users still exist (spot check)
    assert User.get_by_id(1) is not None, "Deleting user 3 should not affect user 1."

def test_delete_by_id_non_existent_user_fails():
    """Tests attempting to delete a user by an ID that does not exist."""
    non_existent_id = 9997

    # --- Pre-check ---
    assert User.get_by_id(non_existent_id) is None, f"Setup failed: User ID {non_existent_id} found unexpectedly."
    initial_count = len(User.get_all())

    # --- Perform Deletion ---
    delete_successful = User.delete_by_id(non_existent_id)
    # The SQL DELETE command will affect 0 rows if the WHERE id=? clause doesn't match.
    # The delete_by_id() method should return False based on cursor.rowcount.
    assert delete_successful is False, "User.delete_by_id() should return False for a non-existent user ID."

    # --- Verification ---
    # Verify the total count of users remains unchanged
    final_count = len(User.get_all())
    assert final_count == initial_count, "Total user count should not change when deleting a non-existent ID."

# Test get_all() method
def test_get_all_users_returns_correct_data():
    """Tests retrieving all users from the database matches the initial sample data."""
    all_users = User.get_all() # Method under test

    # --- Basic Checks ---
    assert isinstance(all_users, list), "User.get_all() should return a list."
    assert len(all_users) == len(SAMPLE_USERS), f"Expected {len(SAMPLE_USERS)} users based on sample data, but got {len(all_users)}."

    # --- Content Verification ---
    # Convert both sample data and fetched data into dictionaries keyed by email for easier comparison,
    # as get_all() might not guarantee order unless explicitly specified (though we added ORDER BY id).
    fetched_users_dict = {user.email: user for user in all_users}
    sample_users_dict = {data['email']: data for data in SAMPLE_USERS}

    assert len(fetched_users_dict) == len(sample_users_dict), "Number of unique emails in fetched data doesn't match sample data."

    # Compare each user from the sample data against the fetched data
    for email, sample_data in sample_users_dict.items():
        assert email in fetched_users_dict, f"Email '{email}' from sample data was not found in the users returned by get_all()."
        fetched_user = fetched_users_dict[email]

        # Verify attributes match
        assert fetched_user.name == sample_data['name']
        assert fetched_user.preference_temperature == sample_data['preference_temperature']
        assert fetched_user.google_oauth_token == sample_data.get('google_oauth_token')
        assert fetched_user.id is not None # All users fetched from DB should have an ID

# Test __repr__ and __eq__ methods
def test_user_representation_string():
    """Tests the __repr__ method for a clear, developer-friendly string representation."""
    user_with_token = User(id=10, name="Test Repr", email="repr@test.com", preference_temperature="gets_hot_easily", google_oauth_token="test_token")
    expected_repr_with_token = "User(id=10, name='Test Repr', email='repr@test.com', preference='gets_hot_easily', google_token_present=True)"
    assert repr(user_with_token) == expected_repr_with_token

    user_no_token = User(id=11, name="Test Repr No Token", email="repr2@test.com", preference_temperature="neutral", google_oauth_token=None)
    expected_repr_no_token = "User(id=11, name='Test Repr No Token', email='repr2@test.com', preference='neutral', google_token_present=False)"
    assert repr(user_no_token) == expected_repr_no_token

    user_no_id = User(name="No ID Repr", email="noid@repr.com")
    expected_repr_no_id = "User(id=None, name='No ID Repr', email='noid@repr.com', preference='neutral', google_token_present=False)"
    assert repr(user_no_id) == expected_repr_no_id

def test_user_equality_comparison():
    """Tests the __eq__ method for accurately comparing User instances."""
    # --- Setup User Instances ---
    # Identical users (simulating fetched vs created)
    user1a = User(id=1, name="Test Eq", email="eq@test.com", preference_temperature="neutral", google_oauth_token="t1")
    user1b = User(id=1, name="Test Eq", email="eq@test.com", preference_temperature="neutral", google_oauth_token="t1")

    # Users differing by one attribute
    user2_diff_id = User(id=2, name="Test Eq", email="eq@test.com", preference_temperature="neutral", google_oauth_token="t1")
    user3_diff_name = User(id=1, name="Test Eq Changed", email="eq@test.com", preference_temperature="neutral", google_oauth_token="t1")
    user4_diff_email = User(id=1, name="Test Eq", email="eq_changed@test.com", preference_temperature="neutral", google_oauth_token="t1")
    user5_diff_pref = User(id=1, name="Test Eq", email="eq@test.com", preference_temperature="gets_cold_easily", google_oauth_token="t1")
    user6_diff_token = User(id=1, name="Test Eq", email="eq@test.com", preference_temperature="neutral", google_oauth_token="t2")
    user7_diff_token_none = User(id=1, name="Test Eq", email="eq@test.com", preference_temperature="neutral", google_oauth_token=None)

    # Users without IDs (unsaved)
    user_no_id_a = User(name="No ID", email="noid@test.com", preference_temperature="neutral", google_oauth_token="t_noid")
    user_no_id_b = User(name="No ID", email="noid@test.com", preference_temperature="neutral", google_oauth_token="t_noid")
    user_no_id_c = User(name="No ID Diff", email="noid@test.com", preference_temperature="neutral", google_oauth_token="t_noid") # Different name

    # --- Assertions ---
    assert (user1a == user1b) is True, "Identical user instances should be equal."
    assert (user1a != user1b) is False, "Identical user instances should not be unequal."

    # Comparisons with differing attributes
    assert (user1a == user2_diff_id) is False, "Users with different IDs should not be equal."
    assert (user1a != user2_diff_id) is True, "Users with different IDs should be unequal."
    assert (user1a == user3_diff_name) is False, "Users with different names should not be equal."
    assert (user1a == user4_diff_email) is False, "Users with different emails should not be equal."
    assert (user1a == user5_diff_pref) is False, "Users with different preferences should not be equal."
    assert (user1a == user6_diff_token) is False, "Users with different google_oauth_tokens should not be equal."
    assert (user1a == user7_diff_token_none) is False, "User with token should not equal user without token (when token differs)."
    assert (user7_diff_token_none == user1a) is False, "User without token should not equal user with token (when token differs)."

    # Comparisons with non-User types
    assert (user1a == "not a user object") is False, "User instance should not be equal to a string."
    # The __eq__ method should return NotImplemented for unsupported types, which results in False for ==
    assert (user1a == None) is False, "User instance should not be equal to None."

    # Comparisons involving None IDs
    assert (user_no_id_a == user_no_id_b) is True, "Unsaved users with identical data should be equal."
    assert (user_no_id_a == user_no_id_c) is False, "Unsaved users with different data should not be equal."
    # Comparison between saved (ID not None) and unsaved (ID is None)
    assert (user1a == user_no_id_a) is False, "Saved user (ID=1) should not be equal to unsaved user (ID=None)."
    assert (user_no_id_a == user1a) is False, "Unsaved user (ID=None) should not be equal to saved user (ID=1)."
