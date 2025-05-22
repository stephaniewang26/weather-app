from flask import Flask
from flask import request
from flask import render_template
import json
import calendar
import math
import os

from models import User_Model
DB_location=f"{os.getcwd()}/yahtzee/Models/yahtzeeDB.db"
Users = User_Model.User(DB_location, "users")
Games = Game_Model.Game(DB_location, "games")
Scorecards = Scorecard_Model.Scorecard(DB_location, scorecard_table_name="scorecard", user_table_name="users", game_table_name="games")

import html_titles
titles_dict = html_titles.get_titles()

import game_controller

def users():
    print(f"request.url={request.url}")

    if request.method == 'GET':
        return render_template('user_details.html', logged_in=False, my_games=True, current_route=request.path,btn_context="create", title=titles_dict["user_details"])
    elif request.method == 'POST':
        # get values inputted ✅
        inputted_username = request.form.get("username")
        inputted_password = request.form.get("password")
        inputted_email = request.form.get("email")
        #format to put into user model create ✅
        inputted_info = {"username":inputted_username,
                         "password":inputted_password,
                         "email":inputted_email}
        print(inputted_info)
        # check if user exists (pass in username) --> if so, return negative feedback ✅
        exists_packet = Users.exists(username=inputted_info["username"])
        if exists_packet["data"] == True:
            print("exists!")
            return render_template('user_details.html', logged_in=False, my_games=True, current_route=request.path,feedback="User already exists!", btn_context="create", title=titles_dict["user_details"])
        # if not, then attempt to create ✅
        else:
            create_packet = Users.create(inputted_info)
            #act depending on if it returns success/error --> if success, then direct to user_games ✅
            if create_packet["status"] == "success":
                all_game_names = game_controller.get_user_game_names(username=create_packet["data"]["username"])

                high_scores_list = game_controller.return_high_scores(create_packet["data"]["username"])

                return render_template('user_games.html', logged_in=True, my_games=True, current_route=request.path, high_scores_list=high_scores_list, title=titles_dict["user_games"], games_list=all_game_names, username=create_packet["data"]["username"])
            #if not, then use feedback from error message and template it in ✅
            else:
                return render_template('user_details.html', logged_in=False, my_games=True, current_route=request.path, feedback=create_packet["data"], btn_context="create", title=titles_dict["user_details"])