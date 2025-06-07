import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useRouter } from 'expo-router';

const Settings = () => {
    const router = useRouter();
    const [selectedPreference, setSelectedPreference] = useState('');
    const [message, setMessage] = useState('');

    useEffect(() => {
        loadUserPreference();
    }, []);

    const loadUserPreference = async () => {
        try {
            const userEmail = await AsyncStorage.getItem('userEmail');
            const IP_ADDRESS = process.env.EXPO_PUBLIC_IP_ADDRESS;
            const response = await fetch(`http://${IP_ADDRESS}:5000/weather?email=${encodeURIComponent(userEmail)}`);
            const data = await response.json();
            setSelectedPreference(data.userPreference);
        } catch (error) {
            console.error('Error loading preference:', error);
        }
    };

    const updatePreference = async (newPreference) => {
        try {
            const userEmail = await AsyncStorage.getItem('userEmail');
            const IP_ADDRESS = process.env.EXPO_PUBLIC_IP_ADDRESS;
            
            const response = await fetch(`http://${IP_ADDRESS}:5000/users/preference`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: userEmail,
                    preference: newPreference
                }),
            });

            if (response.ok) {
                setSelectedPreference(newPreference);
                setMessage('Preference updated successfully!');
            }
        } catch (error) {
            console.error('Error updating preference:', error);
            setMessage('Failed to update preference');
        }
    };

    const handleSignOut = async () => {
    try {
        const userEmail = await AsyncStorage.getItem('userEmail');
        const IP_ADDRESS = process.env.EXPO_PUBLIC_IP_ADDRESS;

        const response = await fetch(`http://${IP_ADDRESS}:5000/users/delete/${userEmail}`);
        console.log(response)
        
        // Sign out from Google
        await GoogleSignin.signOut();
        await AsyncStorage.clear();
        router.replace('/');
    } catch (error) {
        console.error('Error signing out:', error);
    }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Settings</Text>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Temperature Preference</Text>
                <View style={styles.preferenceButtons}>
                    {[
                        { label: "I get cold easily", value: "gets_cold_easily", color: '#2196F3' },
                        { label: "I get hot easily", value: "gets_hot_easily", color: '#FF5722' },
                        { label: "Neutral", value: "neutral", color: '#666' }
                    ].map((pref) => (
                        <TouchableOpacity
                            key={pref.value}
                            style={[
                                styles.preferenceButton,
                                selectedPreference === pref.value && [styles.selectedButton, { backgroundColor: pref.color }]
                            ]}
                            onPress={() => updatePreference(pref.value)}
                        >
                            <Text style={[
                                styles.preferenceText,
                                selectedPreference === pref.value && styles.selectedText
                            ]}>
                                {pref.label}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </View>
            </View>

            {message ? <Text style={styles.message}>{message}</Text> : null}


            <TouchableOpacity 
            style={styles.signOutButton}
            onPress={handleSignOut}
            >
            <Text style={styles.signOutText}>Sign Out</Text>
            </TouchableOpacity>
        </View>
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
        marginBottom: 20,
    },
    section: {
        marginBottom: 20,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    preferenceButtons: {
        gap: 10,
    },
    preferenceButton: {
        backgroundColor: '#f0f0f0',
        padding: 15,
        borderRadius: 10,
    },
    preferenceText: {
        fontSize: 16,
    },
    selectedText: {
        color: 'white',
    },
    message: {
        marginVertical: 10,
        textAlign: 'center',
    },
    signOutButton: {
        backgroundColor: '#dc3545',
        padding: 15,
        borderRadius: 10,
        marginTop: 'auto',
    },
    signOutText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
        textAlign: 'center',
    }
});

export default Settings;