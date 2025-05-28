import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Button } from 'react-native';
import { Link } from 'expo-router'; 


const Home = () => {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        //const response = await fetch('http://192.168.0.134:5000/weather'); // home
        const response = await fetch('http://10.202.1.125:5000/weather'); // trinity guest
        if (!response.ok) {
          throw new Error('Could not retrieve weather data');
        }
        const data = await response.json();
        setWeatherData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <Text>Loading weather data...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text>Error: {error}</Text>
      </View>
    );
  }

  if (!weatherData) {
    return null; // Or a more informative placeholder
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.container}>
        <Link href="/login">LOGIN</Link>
      </View>

      <Text style={styles.title}>Weather Today</Text>

      <Text style={styles.feelsLike}>Feels Like: {weatherData.feelsLike}°C</Text>
      <Text>Low: {weatherData.low}°C / High: {weatherData.high}°C</Text>
      <Text>Recommendation: {weatherData.clothingRecommendation}</Text>

      <Text style={styles.sectionTitle}>Hourly Forecast</Text>
      <View style={styles.hourlyContainer}>
        {weatherData.hourly.map((item, index) => (
          <View key={index} style={styles.hourlyItem}>
            <Text>{item.time}</Text>
            <Text>{item.temperature}°C</Text>
            <Text>{item.icon}</Text>
          </View>
        ))}
      </View>

      <Text style={styles.sectionTitle}>7-Day Forecast</Text>
      <View style={styles.dailyContainer}>
        {weatherData.daily.map((item, index) => (
          <View key={index} style={styles.dailyItem}>
            <Text>{item.day}</Text>
            <Text>H:{item.high}°C / L:{item.low}°C</Text>
            <Text>{item.icon}</Text>
          </View>
        ))}
      </View>

      <Text style={styles.sectionTitle}>Conditions</Text>
      <View style={styles.conditionsContainer}>
        <Text>Wind: {weatherData.conditions.windSpeed}</Text>
        <Text>UV Index: {weatherData.conditions.uvIndex}</Text>
        <Text>Humidity: {weatherData.conditions.humidity}</Text>
        <Text>Air Quality: {weatherData.conditions.airQuality}</Text>
        <Text>Pollen Count: {weatherData.conditions.pollenCount}</Text>
        <Text>{weatherData.conditions.description}</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  feelsLike: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 10,
  },
  hourlyContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  hourlyItem: {
    alignItems: 'center',
  },
  dailyContainer: {
    marginBottom: 10,
  },
  dailyItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 5,
  },
  conditionsContainer: {
    marginTop: 10,
  },
});

export default Home;