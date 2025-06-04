import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Button, TouchableOpacity } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage'
import { Link } from 'expo-router'; 
import Constants from 'expo-constants';


const Home = () => {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCelsius, setIsCelsius] = useState(true);

  const convertToF = (c) => Math.round((c * 9/5) + 32);
  const formatTemp = (temp) => isCelsius ? `${Math.round(temp)}°C` : `${convertToF(temp)}°F`;

  const getClothingRecommendation = (temp, conditions, preference = 'neutral') => {
    const tempC = isCelsius ? temp : (temp - 32) * 5/9;
    let recommendation = [];
  
    // Base layers based on temperature and user preference
    if (preference === 'gets_cold_easily') {
      tempC -= 3; // Adjust temp perception for cold-sensitive users
    } else if (preference === 'gets_hot_easily') {
      tempC += 3; // Adjust temp perception for heat-sensitive users
    }
  
    // Temperature based clothing
    if (tempC < 0) {
      recommendation.push('Heavy winter coat', 'Scarf', 'Gloves', 'Winter hat');
    } else if (tempC < 10) {
      recommendation.push('Warm coat', 'Light scarf', 'Long sleeves');
    } else if (tempC < 20) {
      recommendation.push('Light jacket', 'Long sleeves');
    } else if (tempC < 25) {
      recommendation.push('T-shirt', 'Light sweater');
    } else {
      recommendation.push('T-shirt', 'Shorts');
    }
  
    // Weather condition based items
    if (conditions.includes('rain')) {
      recommendation.push('Umbrella', 'Waterproof jacket');
    }
    if (conditions.includes('snow')) {
      recommendation.push('Snow boots', 'Waterproof gloves');
    }
    if (conditions.includes('wind')) {
      recommendation.push('Windbreaker');
    }
  
    return recommendation;
  };


  // Load saved temperature preference
  useEffect(() => {
    const loadTempPreference = async () => {
      try {
        const savedPreference = await AsyncStorage.getItem('tempUnit');
        if (savedPreference !== null) {
          setIsCelsius(savedPreference === 'celsius');
        }
      } catch (err) {
        console.error('Error loading temperature preference:', err);
      }
    };
    loadTempPreference();
  }, []);

  // Save preference when it changes
  useEffect(() => {
    const saveTempPreference = async () => {
      try {
        await AsyncStorage.setItem('tempUnit', isCelsius ? 'celsius' : 'fahrenheit');
      } catch (err) {
        console.error('Error saving temperature preference:', err);
      }
    };
    saveTempPreference();
  }, [isCelsius]);


  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const IP_ADDRESS = process.env.EXPO_PUBLIC_IP_ADDRESS;
        const userEmail = await AsyncStorage.getItem('userEmail');
        console.log("Fetching weather for email:", userEmail); // Debug log
        
        const response = await fetch(
          `http://${IP_ADDRESS}:5000/weather?email=${encodeURIComponent(userEmail)}`
        );
        
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
        <Link href="/">GOOGLE OAUTH</Link>
      </View>

      <Text style={styles.title}>Weather Today</Text>
      <TouchableOpacity 
      style={styles.unitToggle}
      onPress={() => setIsCelsius(!isCelsius)}
      >
        <Text>{isCelsius ? '°F' : '°C'}</Text>
      </TouchableOpacity>

      <Text style={styles.feelsLike}>
        Feels Like: {formatTemp(weatherData.feelsLike)}
      </Text>
      <Text>
        Low: {formatTemp(weatherData.low)} / High: {formatTemp(weatherData.high)}
      </Text>

      <Text>{weatherData.userPreference}</Text>
      <ScrollView style={styles.container}>
        {/* ...existing code... */}
        
        <View style={styles.recommendationContainer}>
          <Text style={styles.recommendationTitle}>Recommended Clothing:</Text>
          {getClothingRecommendation(
            weatherData.feelsLike, 
            weatherData.conditions,
            weatherData.userPreference // Add this to your weather data fetch
          ).map((item, index) => (
            <Text key={index} style={styles.recommendationItem}>• {item}</Text>
          ))}
        </View>
      </ScrollView>

      <Text style={styles.sectionTitle}>Conditions</Text>
      <View style={styles.conditionsContainer}>
        <Text>Wind: {weatherData.conditions.windSpeed}</Text>
        <Text>UV Index: {weatherData.conditions.uvIndex}</Text>
        <Text>Humidity: {weatherData.conditions.humidity}</Text>
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
  unitToggle: {
    backgroundColor: '#f0f0f0',
    padding: 10,
    borderRadius: 5,
    marginVertical: 10,
    alignSelf: 'center'
  },
  recommendationContainer: {
    padding: 15,
    backgroundColor: '#f5f5f5',
    borderRadius: 10,
    margin: 10,
  },
  recommendationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  recommendationItem: {
    fontSize: 16,
    marginVertical: 2,
  },
});

export default Home;