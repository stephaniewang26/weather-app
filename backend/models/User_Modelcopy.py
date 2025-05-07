#Stephanie Wang
import sqlite3
import random

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
                    WHERE username = '{email}';
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

    #remake the user model stuff lol
#     ------
    
#     def get(self, username=None, id=None):
#         try: 
#             db_connection = sqlite3.connect(self.db_name)
#             cursor = db_connection.cursor()
#             if username != None:
#                 specific_user_query = cursor.execute(f'''
#                                                     SELECT * FROM {self.table_name} 
#                                                     WHERE username = '{username}';''')
#                 specific_user = specific_user_query.fetchall()
#                 if specific_user != []:
#                     return {"status":"success",
#                     "data":self.to_dict(specific_user[0])}
#                 else:
#                     return {"status":"error",
#                     "data":"User does not exist!"}
#             elif id != None:
#                 specific_user_query = cursor.execute(f'''
#                                                     SELECT * FROM {self.table_name} 
#                                                     WHERE id = {id};''')
#                 specific_user = specific_user_query.fetchall()
#                 if specific_user != []:
#                     return {"status":"success",
#                     "data":self.to_dict(specific_user[0])}
#                 else:
#                     return {"status":"error",
#                     "data":"User does not exist!"}
#             else:
#                 return {"status":"error",
#                     "data":"No username or id entered!"}

#         except sqlite3.Error as error:
#             return {"status":"error",
#                     "data":error}
#         finally:
#             db_connection.close()
    
#     def get_all(self): 
#         try: 
#             db_connection = sqlite3.connect(self.db_name)
#             cursor = db_connection.cursor()
#             all_users_query = cursor.execute(f'''SELECT * FROM {self.table_name};''')
#             all_users = all_users_query.fetchall()

#             all_users_list = []
#             for user_tup in all_users:
#                 all_users_list.append(self.to_dict(user_tup))
            
#             return {"status":"success",
#                         "data":all_users_list}
#         except sqlite3.Error as error:
#             return {"status":"error",
#                     "data":error}
#         finally:
#             db_connection.close()

#     def update(self, user_info): 
#         try: 
#             db_connection = sqlite3.connect(self.db_name)
#             cursor = db_connection.cursor()
#             all_ids_query = cursor.execute(f'''SELECT id FROM {self.table_name};''')
#             all_ids = all_ids_query.fetchall()
#             #print(all_ids)
#             #check if id exists
#             if (user_info["id"],) not in all_ids:
#                 return {"status":"error",
#                         "data":"Id does not exist!"}
#             #if id does exist
#             else:
#                 #check if username and email are unique and if username/email/password are correctly formatted
#                 existing_emails_query = cursor.execute(f'''SELECT email FROM {self.table_name};''')
#                 existing_emails = existing_emails_query.fetchall()

#                 original_user_query = cursor.execute(f'''SELECT * FROM {self.table_name} WHERE id = {user_info["id"]};''')
#                 original_user = original_user_query.fetchone()

#                 #email
#                 #if the email doesn't match the current email and is present in the db
#                 if (user_info["email"],) in existing_emails and user_info["email"] != original_user[1]:
#                     return {"status":"error",
#                             "data": "Email address already exists!"}
#                 elif "@" not in user_info["email"]:
#                     return {"status":"error",
#                             "data": "Email address should contain @ character."}
#                 elif "." not in user_info["email"]:
#                     return {"status":"error",
#                             "data": "Email address should contain . character."}
#                 elif " " in user_info["email"]:
#                     return {"status":"error",
#                             "data": "Email address should not contain any spaces."}
#                 #username
#                 #if the username doesn't match the current username and already exists 
#                 elif (self.exists(username=user_info["username"])["data"] == True) and user_info["username"] != original_user[2]:
#                     return {"status":"error",
#                             "data": "Username already exists!"}
#                 elif user_info["username"].isalnum() == False:
#                     for character in user_info["username"]:
#                         if character != "-" and character != "_" and character.isalnum() == False:
#                             return {"status":"error",
#                                     "data":"Username contains forbidden characters!"}
#                     # if "-" not in user_info["username"] and "_" not in user_info["username"]:
#                     #     return {"status":"error",
#                     #             "data":"Username contains forbidden characters!"}
#                 #password
#                 if len(user_info["password"]) < 8:
#                     return {"status":"error",
#                             "data":"Password is too short."}
#                 #update id's info
#                 else:
#                     cursor.execute(f'''
#                     UPDATE {self.table_name}
#                     SET email = '{user_info["email"]}',
#                     username = '{user_info["username"]}',
#                     password = '{user_info["password"]}'
#                     WHERE id = {user_info["id"]};
#                     ''')
#                     db_connection.commit()

#                     updated_user_query = cursor.execute(f'''SELECT * FROM {self.table_name}
#                                                             WHERE id = {user_info["id"]};''')
#                     updated_user = updated_user_query.fetchall()
#                     return {"status":"success",
#                         "data":self.to_dict(updated_user[0])}
            
#         except sqlite3.Error as error:
#             return {"status":"error",
#                     "data":error}
#         finally:
#             db_connection.close()

#     def remove(self, username): 
#         try: 
#             db_connection = sqlite3.connect(self.db_name)
#             cursor = db_connection.cursor()

#             if (self.exists(username=username)["data"] == True):
#                 original_user_info = self.get(username=username)

#                 cursor.execute(f'''
#                 DELETE FROM {self.table_name}
#                 WHERE username = '{username}';
#                 ''')
#                 db_connection.commit()

#                 return {"status":"success",
#                        "data":original_user_info["data"]}
#             else:
#                 return {"status":"error",
#                     "data":"User does not exist!"}
#         except sqlite3.Error as error:
#             return {"status":"error",
#                     "data":error}
#         finally:
#             db_connection.close()

# if __name__ == '__main__':
#     import os
#     print("Current working directory:", os.getcwd())
#     DB_location=f"{os.getcwd()}/Models/yahtzeeDB.db"

#     Users = User(DB_location, "users")
#     Users.initialize_table()

#     self_users=[{"email":"cookie.monster@trinityschoolnyc.org",
#                     "username":"cookieM",
#                     "password":"123TriniT"},
#                     {"email":"justin.gohde@trinityschoolnyc.org",
#                     "username":"justingohde",
#                     "password":"123TriniT"},
#                     {"email":"zelda@trinityschoolnyc.org",
#                     "username":"princessZ",
#                     "password":"123TriniT"},
#                     {"email":"test.user@trinityschoolnyc.org",
#                     "username":"testuser",
#                     "password":"123TriniT"}]
#     results = []
#     for i in range(len(self_users)):#add 4 users to the DB
#         results.append(Users.create(self_users[i])["data"]["username"])
    
#     # '''{"email":"zelda@trinityschoolnyc.org",
#     #     "username":"princessZ",
#     #     "password":"123TriniT"}'''
#     print(self_users[2]["username"])
#     print(Users.get(username=self_users[2]["username"]))
#     original_user_info = Users.get(username=self_users[2]["username"])
#     print(original_user_info["data"]["id"])
    
#     updated_user_info = {
#         "id":original_user_info["data"]["id"],
#         "email":"zelda@trinityschoolnyc.org", 
#         "username":"princessZzzzzzz", #only change
#         "password":"123TriniT"
#     }
#     returned_user = Users.update(updated_user_info)
#     print(returned_user)
#     print(Users.get(username="princessZzzzzzz"))

#     print(Users.remove("justingohde1"))