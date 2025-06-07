from flask import Flask, request, render_template, jsonify
import json
import calendar
import math
import os
import requests  # Import the requests library


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
            recommendation["extras"].extend(["Umbrella", "Waterproof jacket"])
        if 'snow' in conditions_lower:
            recommendation["extras"].extend(["Snow boots", "Warm socks"])
        if 'wind' in conditions_lower:
            recommendation["extras"].append("Windbreaker")

        return recommendation
    
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
        api_key = "127b911f658f0da3fbb3b802caed4866"  # Replace with your actual API key
        city = "Fredericton"  # You can make this a request parameter
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"  # Use metric units

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes

            data = response.json()
            
            clothing_recommendation=self.get_clothing_recommendation(
                round(data["main"]["feels_like"]),
                data["weather"][0]["description"],
                user_preference
            )

            # Extract relevant weather information
            weather_data = {
                "city": city,
                "feelsLike": round(data["main"]["feels_like"]),
                "low": round(data["main"]["temp_min"]),
                "high": round(data["main"]["temp_max"]),
                "userPreference": user_preference,
                "clothingRecommendation": clothing_recommendation,
                "hourly": [],  # You'd need a different API endpoint for hourly data
                "daily": [],  # You'd need a different API endpoint for daily data
                "conditions": {
                    "windSpeed": data["wind"]["speed"],
                    "humidity": data["main"]["humidity"],
                    "description": self.format_description(data["weather"][0]["description"]),
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