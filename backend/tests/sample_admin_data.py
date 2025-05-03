# tests/sample_admin_data.py
from tests.sample_user_data import SAMPLE_USERS  # Import the original sample users

# Create a list of dictionaries representing sample admin data for testing purposes.
# This data is designed to be easily inserted into the 'admins' table
# during the setup phase of the unit tests.
# It includes 2 admins.  One is a super admin.
SAMPLE_ADMINS = [
    {
        "name": "Alice Wonderland",  # Reuse Alice, but make her an admin
        "email": "alice@example.com",
        "is_super_admin": True,
    },
    {
        "name": "Admin Bob",  # A new admin user
        "email": "adminbob@example.com",
        "is_super_admin": False,
    },
]

# Ensure that the sample admins' emails are unique and do not clash with non-admin users in SAMPLE_USERS.
# In this case,  "alice@example.com" is present in both SAMPLE_USERS and SAMPLE_ADMINS.
# "bob@example.com", "charlie@example.com", "diana@example.com", and "ethan@example.com" are only in SAMPLE_USERS.
# "adminbob@example.com" is only in SAMPLE_ADMINS.
