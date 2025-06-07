import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Button, TouchableOpacity } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage'
import { Link, useFocusEffect } from 'expo-router'; 
import Constants from 'expo-constants';


const Home = () => {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCelsius, setIsCelsius] = useState(true);

  const convertToF = (c) => Math.round((c * 9/5) + 32);
  const formatTemp = (temp) => isCelsius ? `${Math.round(temp)}°` : `${convertToF(temp)}°`;

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

  const getWeatherEmoji = (description) => {
    const conditions = description.toLowerCase();
    if (conditions.includes('clear')) return '☀️';
    if (conditions.includes('cloud')) return '☁️';
    if (conditions.includes('rain')) return '🌧️';
    if (conditions.includes('snow')) return '❄️';
    if (conditions.includes('thunder')) return '⛈️';
    if (conditions.includes('mist') || conditions.includes('fog')) return '🌫️';
    if (conditions.includes('drizzle')) return '🌦️';
    return '🌤️'; // default
  };

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

  useFocusEffect(
    React.useCallback(() => {
      fetchWeather();
    }, [])
  );

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
      {/* <View style={styles.container}>
        <Link href="/">GOOGLE OAUTH</Link>
      </View> */}

      <View style={styles.header}>
          <Text style={styles.cityText}>{weatherData.city}</Text>
          <TouchableOpacity 
              style={styles.unitToggle}
              onPress={() => setIsCelsius(!isCelsius)}
          >
              <Text style={styles.unitToggleText}>{isCelsius ? '°F' : '°C'}</Text>
          </TouchableOpacity>
      </View>

      <Text style={styles.title}>Right now</Text>
      <Text>{weatherData.conditions.description}</Text>

      <View style={styles.emojiFLContainer}>
        <Text style={styles.weatherEmoji}>
          {getWeatherEmoji(weatherData.conditions.description)}
        </Text>
        <View style={styles.feelsLikeContainer}>
          <Text style={styles.feelsLikeLabel}>Feels Like</Text>
          <Text style={styles.temperature}>
            {formatTemp(weatherData.feelsLike)}
          </Text>
          <Text style={styles.lowHighLabel}>
            L: {formatTemp(weatherData.low)}  H: {formatTemp(weatherData.high)}
          </Text>
        </View>
      </View>

      <View style={styles.clothingContainer}>
        <Text style={[
          styles.preferenceText, 
          weatherData.userPreference === 'gets_cold_easily' && styles.coldPreference,
          weatherData.userPreference === 'gets_hot_easily' && styles.hotPreference,
          weatherData.userPreference === 'neutral' && styles.neutralPreference,
        ]}>
          {weatherData.userPreference === 'gets_cold_easily' ? 'You get cold easily.' :
          weatherData.userPreference === 'gets_hot_easily' ? 'You get hot easily.' :
          'Your temperature preference is neutral.'}
        </Text>
        <View style={styles.recommendationList}>
          <View style={styles.recommendationItem}>
            <Text style={styles.recommendationLabel}>Top:</Text>
            <Text style={styles.recommendationText}>{weatherData.clothingRecommendation.inner_top}</Text>
          </View>
          <View style={styles.recommendationItem}>
            <Text style={styles.recommendationLabel}>Outerwear:</Text>
            <Text style={styles.recommendationText}>{weatherData.clothingRecommendation.outerwear}</Text>
          </View>
          <View style={styles.recommendationItem}>
            <Text style={styles.recommendationLabel}>Bottoms:</Text>
            <Text style={styles.recommendationText}>{weatherData.clothingRecommendation.bottoms}</Text>
          </View>
          {weatherData.clothingRecommendation.extras.length > 0 && (
            <View style={styles.recommendationItem}>
              <Text style={styles.recommendationLabel}>Remember!</Text>
              <Text style={styles.recommendationText}>
                {weatherData.clothingRecommendation.extras.join(', ')}
              </Text>
            </View>
          )}
        </View>
      </View>

      <Text style={styles.title}>Today</Text>


      <Text style={styles.title}>Conditions</Text>
      <View style={styles.conditionsContainer}>
        <Text>Wind: {weatherData.conditions.windSpeed}</Text>
        <Text>UV Index: {weatherData.conditions.uvIndex}</Text>
        <Text>Humidity: {weatherData.conditions.humidity}</Text>
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
  conditionsContainer: {
    marginTop: 10,
  },
  emojiFLContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'left',
    marginVertical: 20,
  },
  weatherEmoji: {
    fontSize: 80,
    marginRight: 20,
  },
  feelsLikeContainer: {
    alignItems: 'left',
  },
  feelsLikeLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
  },
  temperature: {
    fontSize: 40,
    fontWeight: 'bold',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    marginBottom: 20,
  },
  unitToggle: {
    backgroundColor: '#f0f0f0',
    padding: 10,
    borderRadius: 5,
    minWidth: 40,
    alignItems: 'center',
  },
  headerSpacer: {
    flex: 1,
  },
  unitToggleText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  cityText: {
    fontSize: 16,
    fontWeight: 'bold',
    backgroundColor: '#f0f0f0',
    padding: 10,
    borderRadius: 5,
  },
  lowHighLabel: {
    fontSize: 18,
  },
  clothingContainer: {
    padding: 15,
    backgroundColor: '#f5f5f5',
    borderRadius: 10,
    marginBottom:20,
  },
  recommendationList: {
    gap: 5,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  recommendationLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 10,
    minWidth: 90,
  },
  recommendationText: {
    fontSize: 16,
    flex: 1,
  },
  preferenceText: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'left',
  },
  coldPreference: {
    color: '#2196F3',  // blue
  },
  hotPreference: {
    color: '#FF5722',  // orange/red
  },
  neutralPreference: {
    color: '#666',
  },
});

export default Home;