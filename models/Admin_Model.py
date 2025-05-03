# models/Admin_Model.py
import sqlite3
import os
from typing import Optional, List, Dict, Any, Tuple

# Define the path to the database file (same as User_Model)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(PROJECT_ROOT, 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')

# Ensure the data directory exists
os.makedirs(DB_DIR, exist_ok=True)

class Admin:
    """
    Represents an administrator user in the application.
    Handles database interactions for the 'admins' table.

    Attributes:
        id (Optional[int]): The unique identifier for the admin (Primary Key).
                            This may or may not correspond to a user's ID in the 'users' table.
        name (str): The admin's name.
        email (str): The admin's email address (must be unique).
        is_super_admin (bool): Flag indicating super admin privileges.
    """

    def __init__(self, name: str, email: str, is_super_admin: bool = False, id: Optional[int] = None):
        self.id = id
        self.name = name
        self.email = email
        self.is_super_admin = is_super_admin

    def _get_connection(self) -> sqlite3.Connection:
        """
        Establishes and returns a new database connection.

        Returns:
            A sqlite3.Connection object to the database file.

        Raises:
            sqlite3.Error: If the connection to the database fails.
        """
        os.makedirs(DB_DIR, exist_ok=True)
        try:
            conn = sqlite3.connect(DB_PATH)
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to database at {DB_PATH}: {e}")
            raise

    @classmethod
    def initialize_table(cls):
        """
        Creates the 'admins' table in the database if it doesn't already exist.
        Also creates an index on the email column for faster lookups.
        This method is idempotent.
        """
        os.makedirs(DB_DIR, exist_ok=True)
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    is_super_admin BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_email ON admins (email)")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error during admin table initialization: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def save(self) -> None:
        """
        Saves the current admin instance to the database.
        """
        if self.id is not None:
            raise ValueError("This admin instance already has an ID. Use update() to modify existing admins.")

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO admins (name, email, is_super_admin) VALUES (?, ?, ?)",
                (self.name, self.email, self.is_super_admin)
            )
            self.id = cursor.lastrowid
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"Email '{self.email}' already exists.") from e
        except sqlite3.Error as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, admin_id: int) -> Optional['Admin']:
        """
        Retrieves an admin by their ID.
        """
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, is_super_admin FROM admins WHERE id = ?", (admin_id,))
            row = cursor.fetchone()
            if row:
                return cls(id=row[0], name=row[1], email=row[2], is_super_admin=bool(row[3]))
            return None
        except sqlite3.Error as e:
            print(f"Database error getting admin by id: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_by_email(cls, email: str) -> Optional['Admin']:
        """
        Retrieves an admin by their email.
        """
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, is_super_admin FROM admins WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return cls(id=row[0], name=row[1], email=row[2], is_super_admin=bool(row[3]))
            return None
        except sqlite3.Error as e:
            print(f"Database error getting admin by email: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def update(self) -> bool:
        """
        Updates the admin's details.
        """
        if self.id is None:
            print("Error: Cannot update admin without an ID.")
            return False

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE admins
                SET name = ?, email = ?, is_super_admin = ?
                WHERE id = ?
                """,
                (self.name, self.email, self.is_super_admin, self.id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            conn.rollback()
            print(f"Error: Could not update admin ID {self.id}. Email '{self.email}' might already exist. Details: {e}")
            return False
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error updating admin: {e}")
            return False
        finally:
            conn.close()

    def delete(self) -> bool:
        """
        Deletes the admin from the database.
        """
        if self.id is None:
            print("Error: Cannot delete admin without an ID.")
            return False

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM admins WHERE id = ?", (self.id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Database error deleting admin: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_all(cls) -> List['Admin']:
        """
        Retrieves all admins from the database.
        """
        conn = None
        admins = []
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, is_super_admin FROM admins")
            rows = cursor.fetchall()
            for row in rows:
                admins.append(cls(id=row[0], name=row[1], email=row[2], is_super_admin=bool(row[3])))
            return admins
        except sqlite3.Error as e:
            print(f"Database error getting all admins: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_user_preference_statistics(cls) -> Dict[str, int]:
        """
        Calculates and returns statistics on user temperature preferences.
        This method demonstrates an admin-specific function.

        Returns:
            A dictionary where keys are temperature preference categories
            ('neutral', 'gets_cold_easily', 'gets_hot_easily') and values are the
            number of users in each category.
        """
        conn = None
        stats = {'neutral': 0, 'gets_cold_easily': 0, 'gets_hot_easily': 0}
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT preference_temperature, COUNT(*) FROM users GROUP BY preference_temperature")
            rows = cursor.fetchall()
            for row in rows:
                if row[0] in stats:
                    stats[row[0]] = row[1]
            return stats
        except sqlite3.Error as e:
            print(f"Database error getting user preference statistics: {e}")
            return stats
        finally:
            if conn:
                conn.close()

    def __repr__(self) -> str:
        return (f"Admin(id={self.id}, name='{self.name}', email='{self.email}', "
                f"is_super_admin={self.is_super_admin})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Admin):
            return NotImplemented
        return (self.id == other.id and
                self.name == other.name and
                self.email == other.email and
                self.is_super_admin == other.is_super_admin)


if __name__ == "__main__":
    print(f"Attempting to initialize admin database at: {DB_PATH}")
    try:
        Admin.initialize_table()
        print("Admin table initialization check complete.")

    except Exception as e:
        print(f"An error occurred during script execution: {e}")