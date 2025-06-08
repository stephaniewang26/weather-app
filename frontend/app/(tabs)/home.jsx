import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Button, TouchableOpacity, Dimensions } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage'
import { Link, useFocusEffect } from 'expo-router'; 
import Constants from 'expo-constants';
import Svg, { Path, Circle, Line, Rect, TSpan, Text as SvgText } from 'react-native-svg';


const Home = () => {
  const [currentWeatherData, setCurrentWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCelsius, setIsCelsius] = useState(true);
  const [hourlyForecast, setHourlyForecast] = useState([]);

  const convertToF = (c) => Math.round((c * 9/5) + 32);
  const formatTemp = (temp) => isCelsius ? `${Math.round(temp)}°` : `${convertToF(temp)}°`;

  const HourlyForecast = ({ data, width, height, isCelsius }) => {
    const temps = data.map(h => h.feelsLike);
    const minTemp = Math.min(...temps) - 2;
    const maxTemp = Math.max(...temps) + 2;
    const tempRange = maxTemp - minTemp;
    const graphWidth = Math.max(width, data.length * 80);
    
    // Adjust x-coordinate calculation to start from left
    const points = data.map((hour, i) => ({
      x: (i * 80) + 40,  // Fixed width per point
      y: height - 40 - ((hour.feelsLike - minTemp) / tempRange * (height - 80))
    }));
  
    const linePath = points.map((point, i) => 
      (i === 0 ? `M ${point.x} ${point.y}` : `L ${point.x} ${point.y}`)
    ).join(' ');
  
    return (
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        style={styles.forecastScroll}
      >
        <View style={styles.forecastContainer}>
          <View style={[styles.hourlyLabels, { width: graphWidth }]}>
            {data.map((hour, index) => (
              <View key={index} style={styles.hourlyItem}>
                <Text style={styles.hourlyTime}>{hour.time}</Text>
              </View>
            ))}
          </View>
          <Svg width={graphWidth} height={height}>
            <Path
              d={linePath}
              stroke="#2196F3"
              strokeWidth="2"
              fill="none"
            />
            {points.map((point, i) => (
              <React.Fragment key={i}>
                <Circle
                  cx={point.x}
                  cy={point.y}
                  r="12"
                  fill="white"
                />
                <SvgText
                  x={point.x}
                  y={point.y + 4}
                  fill="#000"
                  fontSize="12"
                  textAnchor="middle"
                >
                  {formatTemp(data[i].feelsLike)}
                </SvgText>
                <SvgText
                  x={point.x}
                  y={point.y - 20}
                  fontSize="16"
                  textAnchor="middle"
                >
                  {getWeatherEmoji(data[i].description)}
                </SvgText>
              </React.Fragment>
            ))}
          </Svg>
        </View>
      </ScrollView>
    );
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
      console.log(data.hourly_forecast_data);
      setCurrentWeatherData(data.current_weather_data);
      setHourlyForecast(data.hourly_forecast_data.hourly_forecast_list);
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

  if (!currentWeatherData) {
    return null; // Or a more informative placeholder
  }

  return (
    <ScrollView style={styles.container}>
      {/* <View style={styles.container}>
        <Link href="/">GOOGLE OAUTH</Link>
      </View> */}

      <View style={styles.header}>
          <Text style={styles.cityText}>{currentWeatherData.city}</Text>
          <TouchableOpacity 
              style={styles.unitToggle}
              onPress={() => setIsCelsius(!isCelsius)}
          >
              <Text style={styles.unitToggleText}>{isCelsius ? '°F' : '°C'}</Text>
          </TouchableOpacity>
      </View>

      <Text style={styles.title}>Right now</Text>
      <Text>{currentWeatherData.conditions.description}</Text>

      <View style={styles.emojiFLContainer}>
        <Text style={styles.weatherEmoji}>
          {getWeatherEmoji(currentWeatherData.conditions.description)}
        </Text>
        <View style={styles.feelsLikeContainer}>
          <Text style={styles.feelsLikeLabel}>Feels Like</Text>
          <Text style={styles.temperature}>
            {formatTemp(currentWeatherData.feelsLike)}
          </Text>
          <Text style={styles.lowHighLabel}>
            L: {formatTemp(currentWeatherData.low)}  H: {formatTemp(currentWeatherData.high)}
          </Text>
        </View>
      </View>

      <View style={styles.clothingContainer}>
        <Text style={[
          styles.preferenceText, 
          currentWeatherData.userPreference === 'gets_cold_easily' && styles.coldPreference,
          currentWeatherData.userPreference === 'gets_hot_easily' && styles.hotPreference,
          currentWeatherData.userPreference === 'neutral' && styles.neutralPreference,
        ]}>
          {currentWeatherData.userPreference === 'gets_cold_easily' ? 'You get cold easily.' :
          currentWeatherData.userPreference === 'gets_hot_easily' ? 'You get hot easily.' :
          'Your temperature preference is neutral.'}
        </Text>
        <View style={styles.recommendationList}>
          <View style={styles.recommendationItem}>
            <Text style={styles.recommendationLabel}>Top:</Text>
            <Text style={styles.recommendationText}>{currentWeatherData.clothingRecommendation.inner_top}</Text>
          </View>
          <View style={styles.recommendationItem}>
            <Text style={styles.recommendationLabel}>Outerwear:</Text>
            <Text style={styles.recommendationText}>{currentWeatherData.clothingRecommendation.outerwear}</Text>
          </View>
          <View style={styles.recommendationItem}>
            <Text style={styles.recommendationLabel}>Bottoms:</Text>
            <Text style={styles.recommendationText}>{currentWeatherData.clothingRecommendation.bottoms}</Text>
          </View>
          {currentWeatherData.clothingRecommendation.extras.length > 0 && (
            <View style={styles.recommendationItem}>
              <Text style={styles.recommendationLabel}>Remember!</Text>
              <Text style={styles.recommendationText}>
                {currentWeatherData.clothingRecommendation.extras.join(', ')}
              </Text>
            </View>
          )}
        </View>
      </View>

      <Text style={styles.title}>Today</Text>
      <HourlyForecast 
        data={hourlyForecast} 
        width={Dimensions.get('window').width - 40}
        height={150}
        isCelsius={isCelsius}
      />


      <Text style={styles.title}>Conditions</Text>
      <View style={styles.conditionsContainer}>
        <Text>Wind: {currentWeatherData.conditions.windSpeed}</Text>
        <Text>UV Index: {currentWeatherData.conditions.uvIndex}</Text>
        <Text>Humidity: {currentWeatherData.conditions.humidity}</Text>
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
  forecastScroll: {
    marginTop: 20,
  },
  hourlyLabels: {
      flexDirection: 'row',
  },
  hourlyItem: {
      alignItems: 'center',
      width: 80,
  },
  hourlyTime: {
      fontSize: 12,
  },
});

export default Home;