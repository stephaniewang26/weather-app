# tests/sample_user_data.py

# A list of dictionaries representing sample user data for testing purposes.
# This data is designed to be easily inserted into the 'users' table
# during the setup phase of the unit tests (e.g., in a pytest fixture).
# It includes exactly 5 users with various preferences and token statuses.

SAMPLE_USERS = [
    {
        "name": "Alice Wonderland",
        "email": "alice@example.com",
        "preference_temperature": "gets_cold_easily", # Example: Gets cold easily
        "google_oauth_token": "token_alice_123"      # Example: Has OAuth token
    },
    {
        "name": "Bob The Builder",
        "email": "bob@example.com",
        "preference_temperature": "neutral",           # Example: Neutral preference
        "google_oauth_token": None                     # Example: No OAuth token
    },
    {
        "name": "Charlie Chaplin",
        "email": "charlie@example.com",
        "preference_temperature": "gets_hot_easily",  # Example: Gets hot easily
        "google_oauth_token": "token_charlie_789"     # Example: Has OAuth token
    },
    {
        "name": "Diana Prince",
        "email": "diana@example.com",
        "preference_temperature": "neutral",           # Example: Neutral preference
        "google_oauth_token": "token_diana_456"      # Example: Has OAuth token
    },
    {
        "name": "Ethan Hunt",
        "email": "ethan@example.com",
        "preference_temperature": "gets_cold_easily", # Example: Gets cold easily
        "google_oauth_token": None                     # Example: No OAuth token
    }
]

# Note: Ensure this list always contains exactly 5 user dictionaries
# as per the requirement.
