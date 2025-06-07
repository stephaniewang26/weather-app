from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
from controllers.User_Controller import UserController  # Import UserController
import requests  # Import the requests library
import os
from dotenv import load_dotenv, dotenv_values

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', '.env')
print(dotenv_path)
load_dotenv(dotenv_path=dotenv_path)  # Load environment variables from .env file
IP_ADDRESS = os.getenv("EXPO_PUBLIC_IP_ADDRESS") # Get the environment variable

# Initialize controllers
user_controller = UserController()

# --- User Routes ---
@app.route('/users', methods=['POST'])
def create_user():
    return user_controller.create_user()

@app.route('/users/exists', methods=['POST'])
def check_user_exists():
    return user_controller.check_user_exists()

@app.route('/users/delete/<email>', methods=['GET'])
def remove_user(email):
    return user_controller.remove_user(email)

@app.route('/users/preference', methods=['PUT'])
def update_preference():
    return user_controller.update_preference()

# --- Weather Data Route ---
@app.route('/weather', methods=['GET'])
def get_weather():
    return user_controller.get_weather()


if __name__ == '__main__':
    #app.run(debug=True, host="192.168.0.134") # home 
    print("ip address",IP_ADDRESS)
    app.run(debug=True, host=IP_ADDRESS) # trinity guest