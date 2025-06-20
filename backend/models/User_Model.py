#Stephanie Wang
import sqlite3
import random
import os

class User:
    def __init__(self, db_name, table_name):
        self.db_name =  db_name
        self.max_safe_id = 9007199254740991 #maximun safe Javascript integer
        self.table_name = table_name #"users"
    
    def initialize_table(self):
        try:
            db_connection = sqlite3.connect(self.db_name)
            cursor = db_connection.cursor()
            schema=f"""
                    CREATE TABLE {self.table_name} (
                        id INTEGER PRIMARY KEY UNIQUE,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        preference_temperature TEXT CHECK(preference_temperature IN ('neutral', 'gets_cold_easily', 'gets_hot_easily')) DEFAULT 'neutral',
                        google_oauth_token TEXT
                    )
                    """
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name};")
            results=cursor.execute(schema)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_email ON users (email)")
            db_connection.commit()
            # Commit the changes to the database
            # print("User table initialized successfully or already exists.") # Optional confirmation message
        except sqlite3.Error as e:
            print(f"Database error during table initialization: {e}")
            # Re-raise the exception to signal failure
            raise
        finally:
            # Ensure the connection is closed even if an error occurred
            if db_connection:
                db_connection.close()
    
    def create(self, user_info):
        try:
            db_connection = sqlite3.connect(self.db_name)
            cursor = db_connection.cursor()

            existing_ids_query = cursor.execute(f"SELECT id FROM {self.table_name};")
            existing_ids = existing_ids_query.fetchall()

            #CHECK IF ID EXISTS AND REROLL IF IT DOES
            user_id_exists = True
            while user_id_exists == True:
                user_id = random.randint(0, self.max_safe_id)
                #user_id = 1 #(used for testing)
                if ((user_id,) not in existing_ids) == True:
                    user_id_exists = False
                else:
                    user_id_exists = True

            user_data = (user_id, user_info["name"], user_info["email"], user_info["preference_temperature"], user_info["google_oauth_token"])
            user_data_dict = self.to_dict(user_data)
            
            cursor.execute(f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?);", user_data)
            db_connection.commit()

            return {"status": "success",
                    "data": user_data_dict
                    }
        except sqlite3.Error as error:
            return {"status":"error",
                    "data":error}
        finally:
            db_connection.close()

    def exists(self, email=None, id=None):
        try: 
            db_connection = sqlite3.connect(self.db_name)
            cursor = db_connection.cursor()
            email_results = []
            id_results = []

            if email != None:
                email_results = cursor.execute(f'''
                    SELECT * FROM {self.table_name}
                    WHERE email = '{email}';
                ''')
                email_results = email_results.fetchall()

            if id != None:
                id_results = cursor.execute(f'''
                    SELECT * FROM {self.table_name}
                    WHERE id = {id};
                ''')
                id_results = id_results.fetchall()

            if len(email_results) != 1 and len(id_results) != 1:
                return {"status": "success",
                    "data": False
                    }
            else:
                return {"status": "success",
                    "data": True
                    }
        
        except sqlite3.Error as error:
            return {"status":"error",
                    "data":error}
        finally:
            db_connection.close()

    def get(self, email=None, id=None):
        try: 
            db_connection = sqlite3.connect(self.db_name)
            cursor = db_connection.cursor()
            if email != None:
                specific_user_query = cursor.execute(f'''
                                                    SELECT * FROM {self.table_name} 
                                                    WHERE email = '{email}';''')
                specific_user = specific_user_query.fetchall()
                if specific_user != []:
                    return {"status":"success",
                    "data":self.to_dict(specific_user[0])}
                else:
                    return {"status":"error",
                    "data":"User does not exist!"}
            elif id != None:
                specific_user_query = cursor.execute(f'''
                                                    SELECT * FROM {self.table_name} 
                                                    WHERE id = {id};''')
                specific_user = specific_user_query.fetchall()
                if specific_user != []:
                    return {"status":"success",
                    "data":self.to_dict(specific_user[0])}
                else:
                    return {"status":"error",
                    "data":"User does not exist!"}
            else:
                return {"status":"error",
                    "data":"No email or id entered!"}

        except sqlite3.Error as error:
            return {"status":"error",
                    "data":error}
        finally:
            db_connection.close()

    def get_all(self): 
        try: 
            db_connection = sqlite3.connect(self.db_name)
            cursor = db_connection.cursor()
            all_users_query = cursor.execute(f'''SELECT * FROM {self.table_name};''')
            all_users = all_users_query.fetchall()

            all_users_list = []
            for user_tup in all_users:
                all_users_list.append(self.to_dict(user_tup))
            
            return {"status":"success",
                        "data":all_users_list}
        except sqlite3.Error as error:
            return {"status":"error",
                    "data":error}
        finally:
            db_connection.close()

    def update(self, user_info): 
        #IN THE FUTURE, THE EMAIL CHECKER SHOULD BE THROUGH OAUTH/VALID EMAIL CHECKER ANYWAY
        try: 
            db_connection = sqlite3.connect(self.db_name)
            cursor = db_connection.cursor()
            all_ids_query = cursor.execute(f'''SELECT id FROM {self.table_name};''')
            all_ids = all_ids_query.fetchall()
            #print(all_ids)
            #check if id exists
            if (user_info["id"],) not in all_ids:
                return {"status":"error",
                        "data":"Id does not exist!"}
            #if id does exist
            else:
                #check if username and email are unique and if username/email/password are correctly formatted
                existing_emails_query = cursor.execute(f'''SELECT email FROM {self.table_name};''')
                existing_emails = existing_emails_query.fetchall()
                
                original_user_query = cursor.execute(f'''SELECT * FROM {self.table_name} WHERE id = {user_info["id"]};''')
                original_user = original_user_query.fetchone()
                
                #email
                #if the email doesn't match the current email and is present in the db
                if (user_info["email"],) in existing_emails and user_info["email"] != original_user[2]:
                    return {"status":"error",
                            "data": "Email address already exists!"}
                elif "@" not in user_info["email"]:
                    return {"status":"error",
                            "data": "Email address should contain @ character."}
                elif "." not in user_info["email"]:
                    return {"status":"error",
                            "data": "Email address should contain . character."}
                elif " " in user_info["email"]:
                    return {"status":"error",
                            "data": "Email address should not contain any spaces."}
                #name
                # Lowk do not need this but just in case
                # elif user_info["name"].isalnum() == False:
                #     for character in user_info["name"]:
                #         if character != "-" and character != "_" and character.isalnum() == False:
                #             return {"status":"error",
                #                     "data":"Name contains forbidden characters!"}
                
                #update id's info
                else:
                    cursor.execute(f'''
                    UPDATE {self.table_name}
                    SET email = '{user_info["email"]}',
                    name = '{user_info["name"]}'
                    WHERE id = {user_info["id"]};
                    ''')
                    db_connection.commit()
                   

                    updated_user_query = cursor.execute(f'''SELECT * FROM {self.table_name}
                                                            WHERE id = {user_info["id"]};''')
                    updated_user = updated_user_query.fetchall()
                    return {"status":"success",
                        "data":self.to_dict(updated_user[0])}
            
        except sqlite3.Error as error:
            return {"status":"error",
                    "data":error}
        finally:
            db_connection.close()

    def update_preference(self, email, new_preference):
        try:
            db_connection = sqlite3.connect(self.db_name)
            cursor = db_connection.cursor()
            
            # Check if user exists
            user_exists = self.exists(email=email)
            if not user_exists["data"]:
                return {
                    "status": "error",
                    "data": "User does not exist"
                }
            
            # Update preference
            cursor.execute(f'''
                UPDATE {self.table_name}
                SET preference_temperature = ?
                WHERE email = ?
            ''', (new_preference, email))
            
            db_connection.commit()
            
            # Get updated user data
            updated_user = self.get(email=email)
            return {
                "status": "success",
                "data": updated_user["data"]
            }
            
        except sqlite3.Error as error:
            return {
                "status": "error",
                "data": str(error)
            }
        finally:
            db_connection.close()

    def to_dict(self, user_tuple):
        '''Utility function which converts the tuple returned from a SQLlite3 database
           into a dictionary
        '''
        user_dict={}
        if user_tuple:
            user_dict["id"]=user_tuple[0]
            user_dict["name"]=user_tuple[1]
            user_dict["email"]=user_tuple[2]
            user_dict["preference_temperature"]=user_tuple[3]
            user_dict["google_oauth_token"]=user_tuple[4]
        return user_dict

    def remove(self, email): 
        try: 
            db_connection = sqlite3.connect(self.db_name)
            cursor = db_connection.cursor()

            if (self.exists(email=email)["data"] == True):
                original_user_info = self.get(email=email)

                cursor.execute(f'''
                DELETE FROM {self.table_name}
                WHERE email = '{email}';
                ''')
                db_connection.commit()

                return {"status":"success",
                       "data":original_user_info["data"]}
            else:
                return {"status":"error",
                    "data":"User does not exist!"}
        except sqlite3.Error as error:
            return {"status":"error",
                    "data":error}
        finally:
            db_connection.close()

if __name__ == '__main__':
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
    
    DB_location=f"{os.getcwd()}/backend/data/database.db"
    user = User(DB_location, "users")
    user.initialize_table()
    user.create(SAMPLE_USERS[0])
    result = user.exists(email=SAMPLE_USERS[0]["email"])
    print(result)

    for user_data in SAMPLE_USERS:
        user.create(user_data)

    created_user = user.get(email="ethan@example.com")
    user_id = created_user["data"]["id"]
    valid_email_format = "ethan@example.com"
    # 2. Attempt to update the user's email with a valid format
    valid_update_data = {
        "id": user_id,
        "name": "Updated Name",
        "email": valid_email_format,
    }
    result = user.update(valid_update_data)
    print(result)

