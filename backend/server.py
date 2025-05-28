from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
from controllers.User_Controller import UserController  # Import UserController
import requests  # Import the requests library
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize controllers
user_controller = UserController()

# --- User Routes ---
@app.route('/users', methods=['POST'])
def create_user():
    return user_controller.create_user()

# --- Weather Data Route ---
@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetches weather data from the OpenWeatherMap API.
    Requires an API key.
    """
    api_key = "127b911f658f0da3fbb3b802caed4866"  # Replace with your actual API key
    city = "New York"  # You can make this a request parameter
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"  # Use metric units

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()

        # Extract relevant weather information
        weather_data = {
            "feelsLike": data["main"]["feels_like"],
            "low": data["main"]["temp_min"],
            "high": data["main"]["temp_max"],
            "clothingRecommendation": "Wear something appropriate for the current temperature.",  # Customize this based on temperature
            "hourly": [],  # You'd need a different API endpoint for hourly data
            "daily": [],  # You'd need a different API endpoint for daily data
            "conditions": {
                "windSpeed": data["wind"]["speed"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "uvIndex": "N/A",  # Not directly available in this API endpoint
                "airQuality": "N/A",  # Not directly available in this API endpoint
                "pollenCount": "N/A",  # Not directly available in this API endpoint
            },
        }

        return jsonify(weather_data), 200

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return jsonify({"error": "Failed to retrieve weather data"}), 500
    except (KeyError, TypeError) as e:
        print(f"Error parsing weather data: {e}")
        return jsonify({"error": "Error processing weather data"}), 500

if __name__ == '__main__':
    #app.run(debug=True, host="192.168.0.134") # home 
    app.run(debug=True, host="10.202.1.125") # trinity guest