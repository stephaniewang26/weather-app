from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
from controllers.User_Controller import UserController
from controllers.Admin_Controller import AdminController

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize controllers
user_controller = UserController()
admin_controller = AdminController()

# --- User Routes ---
@app.route('/users', methods=['POST'])
def create_user():
    return user_controller.create_user()

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return user_controller.get_user(user_id)

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return user_controller.update_user(user_id)

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return user_controller.delete_user(user_id)

@app.route('/users', methods=['GET'])
def get_all_users():
    return user_controller.get_all_users()

@app.route('/login', methods=['POST'])
def login_user():
    return user_controller.login_user()

# --- Admin Routes ---
@app.route('/admins', methods=['POST'])
def create_admin():
    return admin_controller.create_admin()

@app.route('/admins/<int:admin_id>', methods=['GET'])
def get_admin(admin_id):
    return admin_controller.get_admin(admin_id)

@app.route('/admins/<int:admin_id>', methods=['PUT'])
def update_admin(admin_id):
    return admin_controller.update_admin(admin_id)

@app.route('/admins/<int:admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    return admin_controller.delete_admin(admin_id)

@app.route('/admins', methods=['GET'])
def get_all_admins():
    return admin_controller.get_all_admins()

# --- Weather Data Route (Example) ---
@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Example route to simulate fetching weather data.  In a real application,
    you would integrate with a weather API (e.g., OpenWeatherMap, AccuWeather).
    For this example, we'll just return some dummy data.
    """
    dummy_weather_data = {
        "feelsLike": 20,
        "low": 15,
        "high": 25,
        "clothingRecommendation": "Wear a light jacket and jeans.",
        "hourly": [
            {"time": "9 AM", "temperature": 18, "icon": "☀️"},
            {"time": "12 PM", "temperature": 22, "icon": "🌤️"},
            {"time": "3 PM", "temperature": 24, "icon": "☀️"},
            {"time": "6 PM", "temperature": 21, "icon": "🌥️"},
            {"time": "9 PM", "temperature": 19, "icon": "🌙"},
        ],
        "daily": [
            {"day": "Mon", "high": 23, "low": 16, "icon": "☀️"},
            {"day": "Tue", "high": 25, "low": 18, "icon": "🌤️"},
            {"day": "Wed", "high": 22, "low": 17, "icon": "🌧️"},
            {"day": "Thu", "high": 20, "low": 15, "icon": "☁️"},
            {"day": "Fri", "high": 24, "low": 19, "icon": "☀️"},
            {"day": "Sat", "high": 26, "low": 20, "icon": "☀️"},
            {"day": "Sun", "high": 24, "low": 18, "icon": "🌤️"},
        ],
        "conditions": {
            "windSpeed": "60 mph",
            "uvIndex": 6,
            "humidity": "60%",
            "airQuality": "Good",
            "pollenCount": "Medium",
            "description": "Sunny with a moderate breeze.",
        },
    }
    return jsonify(dummy_weather_data), 200

if __name__ == '__main__':
    app.run(debug=True, host="192.168.0.135")

