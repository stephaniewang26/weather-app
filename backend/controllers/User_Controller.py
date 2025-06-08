from flask import Flask, request, render_template, jsonify
import json
import calendar
import math
import os
import requests  # Import the requests library
from dotenv import load_dotenv, dotenv_values
from datetime import datetime
import pytz

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..','frontend', '.env')
load_dotenv(dotenv_path=dotenv_path)  # Load environment variables from .env file
API_KEY = os.getenv("API_KEY") # Get the environment variable


from models.User_Model import User
DB_location=f"{os.getcwd()}/backend/data/database.db"
Users = User(DB_location, "users")

class UserController:
    def create_user(self):
        print(DB_location)
        
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        preference_temperature= data.get('preference_temperature')  # Default to 'neutral' if not provided
        google_oauth_token = data.get('google_oauth_token')

        if not name or not email:
            return jsonify({'error': 'Missing required fields'}), 400

        user_info = {
            "name": name,  # Assuming username is used as name
            "email": email,
            "preference_temperature": preference_temperature,  # Default value
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
        
    def check_user_exists():
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"exists": False}), 400
            
        result = Users.exists(email=email)
        return jsonify({"exists": result["data"]})
    
    def format_description(self,desc):
            # Capitalize first letter and add period if missing
                formatted = desc[0].upper() + desc[1:]
                if not formatted.endswith('.'):
                    formatted += '.'
                return formatted
    
    def get_clothing_recommendation(self,temp, conditions, user_preference):
        # Adjust temperature based on user preference
        adjusted_temp = temp
        if user_preference == 'gets_cold_easily':
            adjusted_temp -= 3
        elif user_preference == 'gets_hot_easily':
            adjusted_temp += 3

        # Initialize recommendation dictionary
        recommendation = {
            "inner_top": "",
            "outerwear": "",
            "bottoms": "",
            "extras": []
        }

        # Inner top recommendations
        if adjusted_temp < 10:
            recommendation["inner_top"] = "Long sleeve thermal shirt"
        elif adjusted_temp < 16:
            recommendation["inner_top"] = "Long sleeve shirt"
        else:
            recommendation["inner_top"] = "T-shirt"

        # Outerwear recommendations
        if adjusted_temp < 0:
            recommendation["outerwear"] = "Heavy winter coat"
        elif adjusted_temp < 7:
            recommendation["outerwear"] = "Warm coat"
        elif adjusted_temp < 10:
            recommendation["outerwear"] = "Light jacket"
        elif adjusted_temp < 13:
            recommendation["outerwear"] = "Light sweater"
        else:
            recommendation["outerwear"] = "No outerwear needed"

        # Bottoms recommendations
        if adjusted_temp < 10:
            recommendation["bottoms"] = "Warm pants"
        elif adjusted_temp < 15:
            recommendation["bottoms"] = "Regular pants"
        else:
            recommendation["bottoms"] = "Shorts or light pants"

        # Additional items based on conditions
        conditions_lower = conditions.lower()
        if 'rain' in conditions_lower:
            recommendation["extras"].extend(["Umbrella"])
        if 'snow' in conditions_lower:
            recommendation["extras"].extend(["Snow boots", "Warm socks"])
        if 'wind' in conditions_lower:
            recommendation["extras"].append("Windbreaker")

        return recommendation
    
    def get_coordinates(self, city):
        """Get latitude and longitude for a city using OpenWeatherMap Geocoding API"""
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        
        try:
            response = requests.get(geocoding_url)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return {
                    "lat": data[0]["lat"],
                    "lon": data[0]["lon"]
                }
            return None
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
        
    def convert_utc_to_est(self, utc_time_str):
        # Convert string to datetime object
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S')
        
        # Set UTC timezone
        utc_time = utc_time.replace(tzinfo=pytz.UTC)
        
        # Convert to EST
        est_tz = pytz.timezone('America/New_York')
        est_time = utc_time.astimezone(est_tz)
        
        # Get hour and minute
        hour = int(est_time.strftime('%I'))  # Remove leading zero
        minute = est_time.strftime('%M')
        ampm = est_time.strftime('%p')
        
        # Return just hour + AM/PM if minute is 00
        if minute == '00':
            return f"{hour}{ampm}"
        return f"{hour}:{minute}{ampm}"
    
    def convert_wind_speed(self, speed_ms):
        """Convert wind speed from m/s to mph"""
        return round(speed_ms * 2.237)

    def get_wind_description(self, speed_mph):
        """Convert wind speed to human readable description"""
        if speed_mph < 1:
            return "Calm."
        elif speed_mph < 8:
            return "Light breeze."
        elif speed_mph < 13:
            return "Gentle breeze."
        elif speed_mph < 19:
            return "Moderate breeze."
        elif speed_mph < 25:
            return "Fresh breeze."
        elif speed_mph < 32:
            return "Strong breeze."
        else:
            return "High winds."
    
    def get_weather(self):
        user_email = request.args.get('email')
        user_preference = 'neutral'  # default

        if user_email:
            # Get user preference from database
            user_result = Users.get(email=user_email)
            if user_result["status"] == "success":
                user_preference = user_result["data"]["preference_temperature"]

        """
        Fetches weather data from the OpenWeatherMap API.
        Requires an API key.
        """
        city = "New York"  # You can make this a request parameter

        try:
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"  # Use metric units
            current_response = requests.get(current_url)
            current_response.raise_for_status()  # Raise an exception for bad status codes
            current_data = current_response.json()
            
            clothing_recommendation=self.get_clothing_recommendation(
                round(current_data["main"]["feels_like"]),
                current_data["weather"][0]["description"],
                user_preference
            )

            wind_speed_mph = self.convert_wind_speed(current_data["wind"]["speed"])

            # Extract relevant weather information
            current_weather_data = {
                "city": city,
                "feelsLike": round(current_data["main"]["feels_like"]),
                "low": round(current_data["main"]["temp_min"]),
                "high": round(current_data["main"]["temp_max"]),
                "userPreference": user_preference,
                "clothingRecommendation": clothing_recommendation,
                "conditions": {
                    "windSpeed": wind_speed_mph,
                    "windDescription": self.get_wind_description(wind_speed_mph),
                    "humidity": current_data["main"]["humidity"],
                    "description": self.format_description(current_data["weather"][0]["description"]),
                    "uvIndex": "N/A",  # Not directly available in this API endpoint
                    "airQuality": "N/A",  # Not directly available in this API endpoint
                    "pollenCount": "N/A",  # Not directly available in this API endpoint
                },
            }

            #FOR THE DAY ------------------------
            coords = self.get_coordinates(city)
            if not coords:
                return jsonify({"error": "Could not get coordinates for city"}), 500

            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}&units=metric"
            forecast_response = requests.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            hourly_forecast = []
            for entry in forecast_data['list'][:8]:
                hourly_forecast.append({
                    "time": self.convert_utc_to_est(entry['dt_txt']),
                    "feelsLike": round(entry['main']['feels_like']),
                    "temp": round(entry['main']['temp']),
                    "description": self.format_description(entry['weather'][0]['description'])
                })

            hourly_forecast_data = {
                "hourly_forecast_list": hourly_forecast,
            }

            combined_data={
                "current_weather_data": current_weather_data,
                "hourly_forecast_data": hourly_forecast_data
            }

            return jsonify(combined_data), 200

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return jsonify({"error": "Failed to retrieve weather data"}), 500
        except (KeyError, TypeError) as e:
            print(f"Error parsing weather data: {e}")
            return jsonify({"error": "Error processing weather data"}), 500

    def remove_user(self, email):
        try:
            result = Users.remove(email=email)
            print("TRYING TO REMOVE")
            if result["status"] == "success":
                return jsonify({"message": "User removed successfully"}), 200
            else:
                return jsonify({"error": result["data"]}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    def update_preference(self):
        try:
            data = request.get_json()
            email = data.get('email')
            new_preference = data.get('preference')

            print(new_preference)
            
            if not email or not new_preference:
                return jsonify({"error": "Missing email or preference"}), 400
                
            result = Users.update_preference(email, new_preference)
            
            if result["status"] == "success":
                return jsonify({"message": "Preference updated successfully"}), 200
            else:
                return jsonify({"error": result["data"]}), 400
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500