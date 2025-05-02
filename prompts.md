# Prompt 1
## Problem Statement
Sometimes, it's hard to know what to wear based on the weather. Regardless of one's age, most people experience this inconvenience at least a few times a month. Generally, this issue does not occur because people don't check the weather; instead, the temperature shown on the weather app often doesn't reflect how it truly feels outside, especially during transitional seasons. This may be due to winds, humidity, precipitation, and other factors that aren't as readily available for interpretation as the "degrees."

[NAME] solves both of these issues by offering a visual recommendation of what to wear for the day, taking both weather factors and user preferences into account. By making the influence of different weather factors accessible and easy-to-understand, [NAME] will provide a way to translate between numbers on a screen and what it actually feels like outside.

## Core Features
An accurate “feels like” temperature that’s displayed by default
Low and high temperatures for the day
A brief text recommendation of what to wear for the day, or what to bring (umbrella, boots, etc) based on user preferences (I get cold easily, I get hot easily)
Hourly weather view
Day-by-day weather view for the week
Conditions for the day (wind speeds, UV index, humidity, air quality, amount of pollen) with a very brief text description of what the numbers actually mean
Google OAuth

## Architecture
Weather App is a client-server application written in React Native.
I am not sure what other languages are best to use. I am familiar with HTML/CSS/JS and Python. I want to be able to publish it to the App Store and the Google Play Store eventually.
The server uses an MVC architecture.
The app needs to use a SQL or JSON database.
Controllers return rendered views using ___.

# Prompt 2
## Problem Statement
Sometimes, it's hard to know what to wear based on the weather. Regardless of one's age, most people experience this inconvenience at least a few times a month. Generally, this issue does not occur because people don't check the weather; instead, the temperature shown on the weather app often doesn't reflect how it truly feels outside, especially during transitional seasons. This may be due to winds, humidity, precipitation, and other factors that aren't as readily available for interpretation as the "degrees."

[NAME] solves both of these issues by offering a visual recommendation of what to wear for the day, taking both weather factors and user preferences into account. By making the influence of different weather factors accessible and easy-to-understand, [NAME] will provide a way to translate between numbers on a screen and what it actually feels like outside.

## Core Features
An accurate “feels like” temperature that’s displayed by default
Low and high temperatures for the day
A visual recommendation of what to wear for the day, or what to bring (umbrella, boots, coat etc) based on user preferences (I get cold easily, I get hot easily)
Hourly weather view
Day-by-day weather view for the week
Conditions for the day (wind speeds, UV index, humidity, air quality, amount of pollen) with a very brief text description of what the numbers actually mean
Google OAuth

## Architecture
Weather App is a client-server application written in React Native.
The backend uses Python Flask. 
The app uses a SQL database.
The app uses a reliable weather API. 
I want to be able to publish it to the App Store and the Google Play Store eventually.
The server uses an MVC architecture.

## LLM Instructions
Create a walking skeleton of this project.
A walking skeleton connects together all the important pieces of a project without worrying about implementing the specific logic behind your application.

Your walking skeleton should include:
Models for each entity
Unit tests for each model method
Controllers for each entity
Views connected to controller routes for each entity
End-to-end tests to verify frontend-backend connections

## Data Storage
A locally-stored db file is used to store information related to each entity.
The database contains multiple tables to store data.
The db is organized in a top-level project folder called /data

## Entity Design
Class models should contain an initialize_table() method to ensure that a table exists in the db for the entity.
Each method in a class model should open, then close a connection to the database to perform the various CRUD operations.

## LLM Instructions
Create the User_Model.py in a folder called /models.
User_Model.py should read and write to the users table in the db file stored in the top-level project /data folder as a database.

Create a /tests folder to organize unit tests written using pytest.
Act as a QA specialist to write test_user_model.py, a robust collection of unit tests to verify the functionality included in User_Model.py
Before each unit test is run, the user table should be deleted and recreated to contain all users included within sample_user_data.py.

The tests folder should include:
- sample_user_data.py, which includes a list of 5 sample users
- test_user_model.py, which includes a robust collection of pytest unit tests for each method included in User_Model.py

Create a README.md file including:
 - Project title
 - Project Overview
 - Folder structure
 - User Class Model diagram using mermaid 
 - instructions for running unit tests




## User Entity
I want to let people use the app without signing in, but I also want to let people sign in with Google OAuth to save their preferences.

A User object should have have the following attributes:
- email: string

The User_Model class should have the following methods:
+ initialize_table()
+ exists(id: int): bool
+ create(user_info: User{}): User{}
+ get_id(id: int): User{}
+ set_google_id(google_id)
+ set_anonymous_session_id(session_id)
+ is_authenticated()
+ get_all(): User[]
+ update(user_info: User{}): User{}
+ remove(username: string): User{}