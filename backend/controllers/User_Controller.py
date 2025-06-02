from flask import Flask, request, render_template, jsonify
import json
import calendar
import math
import os

from models.User_Model import User
DB_location=f"{os.getcwd()}/backend/data/database.db"
Users = User(DB_location, "users")

class UserController:
    def create_user(self):
        print(DB_location)
        
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        google_oauth_token = data.get('google_oauth_token')

        if not name or not email:
            return jsonify({'error': 'Missing required fields'}), 400

        user_info = {
            "name": name,  # Assuming username is used as name
            "email": email,
            "preference_temperature": "neutral",  # Default value
            "google_oauth_token": google_oauth_token
        }

        print(user_info)

        try:
            create_packet = Users.create(user_info)
            print(create_packet)
            if create_packet["status"] == "success":
                return jsonify({'message': 'User created successfully', 'user': create_packet["data"]}), 201
            else:
                return jsonify({'error': create_packet["data"]}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# def users():
#     print(f"request.url={request.url}")

#     if request.method == 'GET':
#         return render_template('user_details.html', logged_in=False, my_games=True, current_route=request.path,btn_context="create", title=titles_dict["user_details"])
#     elif request.method == 'POST':
#         # get values inputted ✅
#         inputted_username = request.form.get("username")
#         inputted_password = request.form.get("password")
#         inputted_email = request.form.get("email")
#         #format to put into user model create ✅
#         inputted_info = {"username":inputted_username,
#                          "password":inputted_password,
#                          "email":inputted_email}
#         print(inputted_info)
#         # check if user exists (pass in username) --> if so, return negative feedback ✅
#         exists_packet = Users.exists(username=inputted_info["username"])
#         if exists_packet["data"] == True:
#             print("exists!")
#             return render_template('user_details.html', logged_in=False, my_games=True, current_route=request.path,feedback="User already exists!", btn_context="create", title=titles_dict["user_details"])
#         # if not, then attempt to create ✅
#         else:
#             create_packet = Users.create(inputted_info)
#             #act depending on if it returns success/error --> if success, then direct to user_games ✅
#             if create_packet["status"] == "success":
#                 all_game_names = game_controller.get_user_game_names(username=create_packet["data"]["username"])

#                 high_scores_list = game_controller.return_high_scores(create_packet["data"]["username"])

#                 return render_template('user_games.html', logged_in=True, my_games=True, current_route=request.path, high_scores_list=high_scores_list, title=titles_dict["user_games"], games_list=all_game_names, username=create_packet["data"]["username"])
#             #if not, then use feedback from error message and template it in ✅
#             else:
#                 return render_template('user_details.html', logged_in=False, my_games=True, current_route=request.path, feedback=create_packet["data"], btn_context="create", title=titles_dict["user_details"])