# models/User_Model.py
import sqlite3
import os
from typing import Optional, List, Dict, Any, Tuple

# Define the path to the database file relative to the project root
# Assumes this script ('User_Model.py') is inside the 'models' folder,
# which is inside the project root.
# os.path.dirname(__file__) gets the directory of the current file ('models')
# os.path.dirname(os.path.dirname(__file__)) goes up one level to the project root
# os.path.join(...) then constructs the path to the 'data' directory and the db file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(PROJECT_ROOT, 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')

# Ensure the data directory exists when the module is loaded.
# This is generally safe for simple scripts but might be handled
# more explicitly during application initialization in larger projects.
os.makedirs(DB_DIR, exist_ok=True)

class User:
    """
    Represents a user in the application. Handles database interactions
    for the 'users' table.

    Attributes:
        id (Optional[int]): The unique identifier for the user (Primary Key).
                            None if the user hasn't been saved to the database yet.
        name (str): The user's full name.
        email (str): The user's email address (must be unique).
        preference_temperature (str): User's subjective temperature preference.
                                      Allowed values: 'neutral', 'gets_cold_easily', 'gets_hot_easily'.
                                      Defaults to 'neutral'.
        google_oauth_token (Optional[str]): Stores the Google OAuth token if the user
                                            authenticated via Google. Defaults to None.
    """
    def __init__(self, name: str, email: str, preference_temperature: str = 'neutral', google_oauth_token: Optional[str] = None, id: Optional[int] = None):
        """
        Initializes a new User instance.

        Args:
            name: The user's name.
            email: The user's email address.
            preference_temperature: The user's temperature preference. Must be one of
                                    'neutral', 'gets_cold_easily', or 'gets_hot_easily'.
                                    Defaults to 'neutral'.
            google_oauth_token: The Google OAuth token (optional).
            id: The user's unique ID (typically assigned by the database, should
                usually be None when creating a new user object).

        Raises:
            ValueError: If `preference_temperature` is not one of the allowed values.
        """
        # Validate preference_temperature upon initialization
        allowed_prefs = ['neutral', 'gets_cold_easily', 'gets_hot_easily']
        if preference_temperature not in allowed_prefs:
            raise ValueError(f"preference_temperature must be one of {allowed_prefs}")

        self.id = id
        self.name = name
        self.email = email
        self.preference_temperature = preference_temperature
        self.google_oauth_token = google_oauth_token

    def _get_connection(self) -> sqlite3.Connection:
        """
        Establishes and returns a new database connection.
        Ensures the data directory exists before connecting.

        Returns:
            A sqlite3.Connection object to the database file.

        Raises:
            sqlite3.Error: If the connection to the database fails.
        """
        # Ensure the directory exists before attempting to connect.
        # This adds robustness in case the directory gets deleted unexpectedly.
        os.makedirs(DB_DIR, exist_ok=True)
        try:
            # Connect to the SQLite database.
            # Consider adding timeout or other connection parameters if needed for robustness.
            conn = sqlite3.connect(DB_PATH, timeout=10) # Example timeout
            # Optional: Enable foreign key constraints if your schema uses them.
            # conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to database at {DB_PATH}: {e}")
            # Re-raise the exception to signal that the connection could not be established.
            raise

    @classmethod
    def initialize_table(cls):
        """
        Creates the 'users' table in the database if it doesn't already exist.
        Also creates an index on the email column for faster lookups.
        This method is idempotent (safe to call multiple times).
        Ensures the data directory exists.

        Raises:
            sqlite3.Error: If there's an issue executing SQL commands during table creation.
        """
        # Ensure directory exists before connecting
        os.makedirs(DB_DIR, exist_ok=True)
        conn = None # Initialize conn to None to handle potential connection errors
        try:
            # Establish connection using the instance method logic
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # SQL command to create the table with constraints
            # Using IF NOT EXISTS makes the operation idempotent
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    preference_temperature TEXT CHECK(preference_temperature IN ('neutral', 'gets_cold_easily', 'gets_hot_easily')) DEFAULT 'neutral',
                    google_oauth_token TEXT
                )
            """)

            # SQL command to create an index on the email column for efficiency
            # Using IF NOT EXISTS makes this idempotent as well
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_email ON users (email)")

            # Commit the changes to the database
            conn.commit()
            # print("User table initialized successfully or already exists.") # Optional confirmation message
        except sqlite3.Error as e:
            print(f"Database error during table initialization: {e}")
            # Re-raise the exception to signal failure
            raise
        finally:
            # Ensure the connection is closed even if an error occurred
            if conn:
                conn.close()

    def save(self) -> None:
        """
        Saves the current user instance as a new row in the 'users' table.
        Requires the user instance to NOT have an ID (i.e., self.id must be None).
        Sets the instance's `id` attribute to the new row's ID upon successful insertion.

        Raises:
            ValueError: If the user instance already has an `id` attribute set.
            ValueError: If the email address already exists in the database (due to UNIQUE constraint).
            sqlite3.Error: For other database-related errors during insertion.
        """
        if self.id is not None:
            # Prevent attempting to re-insert a user that might already exist or has an ID assigned
            raise ValueError("This user instance already has an ID. Use update() to modify existing users.")

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # SQL command to insert a new user
            cursor.execute(
                "INSERT INTO users (name, email, preference_temperature, google_oauth_token) VALUES (?, ?, ?, ?)",
                (self.name, self.email, self.preference_temperature, self.google_oauth_token)
            )
            # Retrieve the auto-generated ID of the newly inserted row
            self.id = cursor.lastrowid
            # Commit the transaction
            conn.commit()
        except sqlite3.IntegrityError as e:
            # This error typically occurs if the UNIQUE constraint on 'email' is violated
            conn.rollback() # Roll back the transaction on error
            print(f"Error: Could not save user. Email '{self.email}' likely already exists. Details: {e}")
            # Re-raise as a more specific ValueError for easier handling by the caller
            raise ValueError(f"Email '{self.email}' already exists.") from e
        except sqlite3.Error as e:
            # Handle other potential database errors
            conn.rollback() # Roll back the transaction
            print(f"Database error during save: {e}")
            raise # Re-raise the original SQLite error
        finally:
            # Ensure the connection is closed
            conn.close()

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """
        Retrieves a single user from the database by their unique ID.

        Args:
            user_id: The integer ID of the user to retrieve.

        Returns:
            A User instance if a user with the given ID is found, otherwise None.
            Returns None if a database error occurs during retrieval.
        """
        conn = None
        try:
            # Establish connection
            conn = sqlite3.connect(DB_PATH) # Consider using cls()._get_connection() if needed
            cursor = conn.cursor()
            # SQL command to select user by ID
            cursor.execute("SELECT id, name, email, preference_temperature, google_oauth_token FROM users WHERE id = ?", (user_id,))
            # Fetch one row
            row = cursor.fetchone()
            if row:
                # If a row is found, create and return a User instance from the data
                return cls(id=row[0], name=row[1], email=row[2], preference_temperature=row[3], google_oauth_token=row[4])
            else:
                # If no row is found, return None
                return None
        except sqlite3.Error as e:
            # Log the error and return None if retrieval fails
            print(f"Database error during get_by_id for ID {user_id}: {e}")
            return None
        finally:
            # Ensure the connection is closed
            if conn:
                conn.close()

    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """
        Retrieves a single user from the database by their unique email address.

        Args:
            email: The email address string of the user to retrieve.

        Returns:
            A User instance if a user with the given email is found, otherwise None.
            Returns None if a database error occurs during retrieval.
        """
        conn = None
        try:
            # Establish connection
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # SQL command to select user by email (case-sensitive by default in SQLite)
            cursor.execute("SELECT id, name, email, preference_temperature, google_oauth_token FROM users WHERE email = ?", (email,))
            # Fetch one row
            row = cursor.fetchone()
            if row:
                # If a row is found, create and return a User instance
                return cls(id=row[0], name=row[1], email=row[2], preference_temperature=row[3], google_oauth_token=row[4])
            else:
                # If no row is found, return None
                return None
        except sqlite3.Error as e:
            # Log the error and return None
            print(f"Database error during get_by_email for email {email}: {e}")
            return None
        finally:
            # Ensure the connection is closed
            if conn:
                conn.close()

    def update(self) -> bool:
        """
        Updates the details of an existing user in the database based on the instance's current attribute values.
        Requires the user instance to have a valid `id` attribute.

        Returns:
            True if the update successfully modified exactly one row (i.e., the user was found and updated).
            False if the user ID was not found, if the update failed due to a constraint (e.g., duplicate email),
            or if a database error occurred. Returns False if the instance's `id` is None.
        """
        if self.id is None:
            # Cannot update a user without knowing their ID
            print("Error: Cannot update user without an ID. Use save() for new users.")
            return False

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # SQL command to update user details based on ID
            cursor.execute(
                """
                UPDATE users
                SET name = ?, email = ?, preference_temperature = ?, google_oauth_token = ?
                WHERE id = ?
                """,
                (self.name, self.email, self.preference_temperature, self.google_oauth_token, self.id)
            )
            # Commit the transaction
            conn.commit()
            # Check if any row was actually affected by the update
            # cursor.rowcount gives the number of rows modified by the last execute statement.
            # It should be 1 if the user with self.id existed and was updated.
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            # Handle potential unique constraint violation if the email is being changed to an existing one
            conn.rollback()
            print(f"Error: Could not update user ID {self.id}. Email '{self.email}' might already exist for another user. Details: {e}")
            return False
        except sqlite3.Error as e:
            # Handle other potential database errors
            conn.rollback()
            print(f"Database error during update for user ID {self.id}: {e}")
            return False
        finally:
            # Ensure the connection is closed
            conn.close()

    @classmethod
    def delete_by_id(cls, user_id: int) -> bool:
        """
        Deletes a user from the database by their unique ID.

        Args:
            user_id: The integer ID of the user to delete.

        Returns:
            True if exactly one row was deleted (i.e., the user was found and deleted).
            False if no user with the given ID was found, or if a database error occurred.
        """
        conn = None
        try:
            # Establish connection
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # SQL command to delete user by ID
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            # Commit the transaction
            conn.commit()
            # Check if any row was actually deleted
            # cursor.rowcount should be 1 if the user existed, 0 otherwise.
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            # Handle potential database errors
            if conn: # Check if conn was successfully created before rollback attempt
                conn.rollback()
            print(f"Database error during delete_by_id for ID {user_id}: {e}")
            return False
        finally:
            # Ensure the connection is closed
            if conn:
                conn.close()

    @classmethod
    def get_all(cls) -> List['User']:
        """
        Retrieves all users from the 'users' table.

        Returns:
            A list of User instances, ordered by ID.
            Returns an empty list if no users are found or if a database error occurs.
        """
        conn = None
        users = [] # Initialize an empty list to store results
        try:
            # Establish connection
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # SQL command to select all users, ordered by ID for consistency
            cursor.execute("SELECT id, name, email, preference_temperature, google_oauth_token FROM users ORDER BY id")
            # Fetch all resulting rows
            rows = cursor.fetchall()
            # Create a User instance for each row and append to the list
            for row in rows:
                users.append(cls(id=row[0], name=row[1], email=row[2], preference_temperature=row[3], google_oauth_token=row[4]))
            return users
        except sqlite3.Error as e:
            # Log the error and return an empty list
            print(f"Database error during get_all: {e}")
            return [] # Return empty list on error
        finally:
            # Ensure the connection is closed
            if conn:
                conn.close()

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the User object.
        Useful for debugging and logging.
        """
        # Indicate whether the google_oauth_token is present without showing the token itself
        token_present = self.google_oauth_token is not None
        return (f"User(id={self.id}, name='{self.name}', email='{self.email}', "
                f"preference='{self.preference_temperature}', google_token_present={token_present})")

    def __eq__(self, other: object) -> bool:
        """
        Checks for equality between two User instances.
        Two instances are considered equal if all their corresponding attributes match.
        Useful primarily for testing purposes.

        Args:
            other: The object to compare against.

        Returns:
            True if `other` is a User instance and all attributes match, False otherwise.
        """
        # Check if the other object is an instance of User
        if not isinstance(other, User):
            # Return NotImplemented to indicate comparison is not supported for this type pair
            return NotImplemented
        # Compare all relevant attributes. Handles cases where ID might be None (for unsaved users).
        return (self.id == other.id and
                self.name == other.name and
                self.email == other.email and
                self.preference_temperature == other.preference_temperature and
                self.google_oauth_token == other.google_oauth_token)

# Example of initializing the table when the module is run directly
# This is generally better handled explicitly in your application's main setup
# script or a dedicated database initialization script.
# if __name__ == "__main__":
#     print(f"Attempting to initialize database at: {DB_PATH}")
#     try:
#         User.initialize_table()
#         print("User table initialization check complete.")
#         # Example usage:
#         # user = User(name="Test User", email="test@example.com")
#         # user.save()
#         # print(f"Saved user: {user}")
#         # all_users = User.get_all()
#         # print(f"All users: {all_users}")
#     except Exception as e:
#         print(f"An error occurred during script execution: {e}")

