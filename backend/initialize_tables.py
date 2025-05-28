from flask import Flask, request, render_template, jsonify
import json
import calendar
import math
import os

from models.User_Model import User
DB_location=f"{os.getcwd()}/backend/data/database.db"
Users = User(DB_location, "users")

Users.initialize_table()