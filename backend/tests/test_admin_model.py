# tests/test_admin_model.py
import pytest
import sqlite3
import os
import sys

# Add the project root directory to the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from models.Admin_Model import Admin, DB_PATH, DB_DIR  # Import the Admin model
from models.User_Model import User
from tests.sample_user_data import SAMPLE_USERS  # Import sample user data
from tests.sample_admin_data import SAMPLE_ADMINS

# --- Test Fixture ---
@pytest.fixture(scope="function")
def setup_teardown_database():
    """
    Pytest fixture to set up and tear down the database before and after each test function.
    This ensures a clean and consistent database state for each test.  This fixture now
    also initializes the users table, and populates both users and admins.
    """
    # --- Setup Phase ---
    try:
        # Ensure the database directory exists
        os.makedirs(DB_DIR, exist_ok=True)

        # Delete the database file if it exists
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

        # Initialize the 'users' table (assuming User.initialize_table() exists)
        User.initialize_table()

        # Initialize the 'admins' table
        Admin.initialize_table()

        # Populate the 'users' table with sample data
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for user_data in SAMPLE_USERS:
            cursor.execute(
                "INSERT INTO users (name, email, preference_temperature, google_oauth_token) VALUES (?, ?, ?, ?)",
                (user_data['name'], user_data['email'], user_data['preference_temperature'], user_data.get('google_oauth_token')),
            )
        conn.commit()

        # Populate the 'admins' table with sample data
        for admin_data in SAMPLE_ADMINS:
            cursor.execute(
                "INSERT INTO admins (name, email, is_super_admin) VALUES (?, ?, ?)",
                (admin_data['name'], admin_data['email'], admin_data['is_super_admin']),
            )
        conn.commit()
        conn.close()

    except Exception as e:
        pytest.fail(f"Database setup failed: {e}")

    # --- Yield to Test ---
    yield  # Control is passed to the test function

    # --- Teardown Phase ---
    # Optional:  Remove the database file after the tests.
    # try:
    #     if os.path.exists(DB_PATH):
    #         os.remove(DB_PATH)
    # except Exception as e:
    #     print(f"Error during teardown: {e}")



# --- Test Functions ---

def test_admin_init_valid():
    """Tests successful initialization of an Admin object with valid data."""
    admin = Admin(name="Test Admin", email="admin@test.com", is_super_admin=True)
    assert admin.name == "Test Admin"
    assert admin.email == "admin@test.com"
    assert admin.is_super_admin is True
    assert admin.id is None


def test_initialize_table_idempotency(setup_teardown_database):
    """Tests that calling initialize_table multiple times doesn't cause errors."""
    try:
        Admin.initialize_table()  # Call it again
        # Check if table exists and has correct columns
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admins';")
        assert cursor.fetchone() is not None
        cursor.execute("PRAGMA table_info(admins);")
        columns = [row[1] for row in cursor.fetchall()]
        expected_columns = {'id', 'name', 'email', 'is_super_admin'}
        assert set(columns) == expected_columns
        conn.close()
    except Exception as e:
        pytest.fail(f"initialize_table idempotency test failed: {e}")



def test_save_new_admin_success(setup_teardown_database):
    """Tests saving a new admin successfully."""
    admin = Admin(name="New Admin", email="newadmin@test.com", is_super_admin=False)
    admin.save()
    assert admin.id is not None
    # Verify the data in the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, is_super_admin FROM admins WHERE id = ?", (admin.id,))
    row = cursor.fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "New Admin"
    assert row[1] == "newadmin@test.com"
    assert row[2] == 0  # 0 for False


def test_save_admin_duplicate_email_raises_error(setup_teardown_database):
    """Tests that saving an admin with a duplicate email raises a ValueError."""
    admin = Admin(name="Duplicate Admin", email="alice@example.com", is_super_admin=True)  # Alice's email
    with pytest.raises(ValueError, match="already exists"):
        admin.save()



def test_get_admin_by_id_existing_admin(setup_teardown_database):
    """Tests retrieving an admin by their ID."""
    # Assuming Alice is admin with id 1 from setup
    admin = Admin.get_by_id(1)
    assert admin is not None
    assert admin.name == "Alice Wonderland"
    assert admin.email == "alice@example.com"
    assert admin.is_super_admin is True


def test_get_admin_by_id_non_existent_admin(setup_teardown_database):
    """Tests retrieving a non-existent admin by ID."""
    admin = Admin.get_by_id(999)
    assert admin is None



def test_get_admin_by_email_existing_admin(setup_teardown_database):
    """Tests retrieving an admin by their email."""
    admin = Admin.get_by_email("alice@example.com")
    assert admin is not None
    assert admin.name == "Alice Wonderland"
    assert admin.email == "alice@example.com"
    assert admin.is_super_admin is True



def test_get_admin_by_email_non_existent_admin(setup_teardown_database):
    """Tests retrieving a non-existent admin by email."""
    admin = Admin.get_by_email("nonexistent@example.com")
    assert admin is None



def test_update_admin_success(setup_teardown_database):
    """Tests updating an admin's details successfully."""
    admin = Admin.get_by_email("adminbob@example.com")  # Get Bob
    assert admin is not None
    admin.name = "Robert Bob"
    admin.is_super_admin = True
    assert admin.update() is True
    # Verify the update in the database
    updated_admin = Admin.get_by_id(admin.id)
    assert updated_admin is not None
    assert updated_admin.name == "Robert Bob"
    assert updated_admin.is_super_admin is True



def test_update_admin_duplicate_email_fails(setup_teardown_database):
    """Tests updating an admin's email to an existing email fails."""
    admin = Admin.get_by_email("adminbob@example.com") #get bob
    assert admin is not None
    admin.email = "alice@example.com"  # Try to change to Alice's email
    assert admin.update() is False #update should return false
    #verify bob's email has not changed
    original_admin = Admin.get_by_email("adminbob@example.com")
    assert original_admin is not None
    assert original_admin.email == "adminbob@example.com"



def test_update_admin_nonexistent_id_fails(setup_teardown_database):
    """Tests updating a non-existent admin."""
    admin = Admin(id=999, name="NonExistent", email="nonexistent@example.com", is_super_admin=False)
    assert admin.update() is False



def test_delete_admin_success(setup_teardown_database):
    """Tests deleting an admin successfully."""
    admin = Admin.get_by_email("adminbob@example.com")  # Get Bob
    assert admin is not None
    admin_id = admin.id
    assert admin.delete() is True
    # Verify deletion
    deleted_admin = Admin.get_by_id(admin_id)
    assert deleted_admin is None



def test_delete_admin_nonexistent_id_fails(setup_teardown_database):
    """Tests deleting a non-existent admin."""
    admin = Admin(id=999, name="NonExistent", email="nonexistent@example.com", is_super_admin=False)
    assert admin.delete() is False



def test_get_all_admins(setup_teardown_database):
    """Tests retrieving all admins."""
    admins = Admin.get_all()
    assert isinstance(admins, list)
    assert len(admins) == 2  # We have 2 admins in SAMPLE_ADMINS
    # Check the content of the first admin
    assert admins[0].name == "Alice Wonderland"
    assert admins[0].email == "alice@example.com"
    assert admins[0].is_super_admin is True
    # Check the content of the second admin
    assert admins[1].name == "Admin Bob"
    assert admins[1].email == "adminbob@example.com"
    assert admins[1].is_super_admin is False



def test_get_user_preference_statistics(setup_teardown_database):
    """Tests retrieving user preference statistics."""
    conn = sqlite3.connect(DB_PATH) #open connection
    cursor = conn.cursor() # create cursor
    stats = {}
    try:
        stats = Admin.get_user_preference_statistics()
        assert isinstance(stats, dict)
        assert stats["neutral"] == 2
        assert stats["gets_cold_easily"] == 2
        assert stats["gets_hot_easily"] == 1
        # Ensure the admin user is not counted in the user preferences.

        cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'alice@example.com'")
        alice_count = cursor.fetchone()[0]

        assert alice_count == 1 #alice is in users table

        cursor.execute("SELECT COUNT(*) FROM admins WHERE email = 'alice@example.com'")
        alice_admin_count = cursor.fetchone()[0]

        assert alice_admin_count == 1 # alice is in admins table
    finally:
        conn.close()  # Ensure connection is closed in a finally block



def test_admin_repr(setup_teardown_database):
    """Tests the __repr__ method of the Admin class."""
    admin = Admin.get_by_email("alice@example.com")
    expected_repr = "Admin(id=1, name='Alice Wonderland', email='alice@example.com', is_super_admin=True)"
    assert repr(admin) == expected_repr



def test_admin_eq(setup_teardown_database):
    """Tests the __eq__ method of the Admin class."""
    admin1 = Admin.get_by_email("alice@example.com")
    admin2 = Admin.get_by_email("alice@example.com")
    admin3 = Admin.get_by_email("adminbob@example.com")
    assert admin1 == admin2
    assert admin1 != admin3
    assert admin1 != "not an admin"