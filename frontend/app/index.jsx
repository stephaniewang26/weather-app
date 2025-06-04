import React, { useState, useEffect } from 'react'
import AsyncStorage from '@react-native-async-storage/async-storage'
import { View, Text, TextInput, Button, StyleSheet, TouchableOpacity } from 'react-native';
import { Link, useRouter } from 'expo-router'; 
import Constants from 'expo-constants';
import {
    GoogleSignin,
    GoogleSigninButton,
    statusCodes,
} from '@react-native-google-signin/google-signin';

const WEB_CLIENT_ID = process.env.EXPO_PUBLIC_WEB_CLIENT_ID;
const IOS_CLIENT_ID = process.env.EXPO_PUBLIC_IOS_CLIENT_ID;

GoogleSignin.configure({
    webClientId: WEB_CLIENT_ID, // client ID of type WEB for your server. Required to get the `idToken` on the user object, and for offline access.
    scopes: ['https://www.googleapis.com/auth/drive.readonly'], // what API you want to access on behalf of the user, default is email and profile
    offlineAccess: true, // if you want to access Google API on behalf of the user FROM YOUR SERVER
    forceCodeForRefreshToken: true, // [Android] related to `serverAuthCode`, read the docs link below *.
    iosClientId: IOS_CLIENT_ID, // [iOS] if you want to specify the client ID of type iOS (otherwise, it is taken from GoogleService-Info.plist)
});

const google_oauth = () => {
    const router = useRouter();
    const [message, setMessage] = useState('');
    const [selectedPreference, setSelectedPreference] = useState('');
    const [isSignedIn, setIsSignedIn] = useState(false);

    useEffect(() => {
        const checkSignIn = async () => {
            try {
                const isSignedIn = await GoogleSignin.hasPreviousSignIn();
                console.log("Checking previous sign in:", isSignedIn);
                
                if (isSignedIn) {
                    try {
                        // Get current user with silent sign in
                        const userInfo = await GoogleSignin.signInSilently();
                        console.log("Silent sign in userInfo:", userInfo);
                        
                        if (userInfo) {
                            // Store user info in AsyncStorage
                            await AsyncStorage.setItem('userEmail', userInfo.data.user.email);
                            
                            setIsSignedIn(true);
                            router.replace('/home');
                        } else {
                            console.log("No valid user info found");
                            await GoogleSignin.signOut();
                            await AsyncStorage.clear();
                        }
                    } catch (error) {
                        console.error("Silent sign in failed:", error);
                        // Clear tokens and storage on error
                        await GoogleSignin.signOut();
                        await AsyncStorage.clear();
                    }
                }
            } catch (error) {
                console.error("Error checking sign in status:", error);
                await AsyncStorage.clear();
            }
        };
    
        checkSignIn();
    }, []);

    const PreferenceSelector = () => (
        <View style={styles.preferenceContainer}>
            <Text style={styles.preferenceTitle}>Select your temperature preference:</Text>
            {[
                { label: "I get cold easily", value: "gets_cold_easily" },
                { label: "I get hot easily", value: "gets_hot_easily" },
                { label: "Neutral", value: "neutral" }
            ].map((pref) => (
                <TouchableOpacity
                    key={pref.value}
                    style={[
                        styles.preferenceButton,
                        selectedPreference === pref.value && styles.selectedButton
                    ]}
                    onPress={() => setSelectedPreference(pref.value)}
                >
                    <Text style={styles.preferenceText}>{pref.label}</Text>
                </TouchableOpacity>
            ))}
        </View>
    );

    const signIn = async () => {
        try {
            if (!selectedPreference) {
                setMessage('Please select a temperature preference');
                return;
            }

            await GoogleSignin.hasPlayServices();
            const userInfo = await GoogleSignin.signIn();
            console.log(userInfo)

            if (userInfo.type == 'success') {
                try {
                    const IP_ADDRESS = process.env.EXPO_PUBLIC_IP_ADDRESS;
                    const response = await fetch(`http://${IP_ADDRESS}:5000/users`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: userInfo.data.user.name,
                            email: userInfo.data.user.email,
                            preference_temperature: selectedPreference,
                            google_oauth_token: userInfo.data.idToken
                        }),
                    });

                    const data = await response.json();

                    if (response.ok) {
                        setMessage('User created successfully!');
                        setIsSignedIn(true);
                        // Store user info in AsyncStorage
                        await AsyncStorage.setItem('userEmail', userInfo.data.user.email);
                        // Navigate to main app screen
                        router.replace('/home');
                    } else {
                        const data = await response.json();
                        setMessage(data.error || 'Failed to create user');
                    }
                } catch (error) {
                    setMessage('Failed to connect to the server.');
                    console.error("Server Error:", error);
                }
            }
        } catch (error) {
            if (error.code === statusCodes.SIGN_IN_CANCELLED) {
                setMessage('Sign-in cancelled by user');
            } else if (error.code === statusCodes.IN_PROGRESS) {
                setMessage('Sign-in in progress');
            } else if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
                setMessage('Play Services not available');
            } else {
                setMessage('Error signing in');
                console.error("Google Sign-In Error:", error);
            }
        }
    };  

    return (
    <View style={styles.container}>
        <PreferenceSelector />
        <GoogleSigninButton
            size={GoogleSigninButton.Size.Wide}
            color={GoogleSigninButton.Color.Dark}
            onPress={signIn}
            disabled={!selectedPreference}
        />
        {message ? <Text>{message}</Text> : null}
    </View>
    )
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
    },
    preferenceContainer: {
        width: '100%',
        alignItems: 'center',
    },
    preferenceTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 20,
    },
    preferenceButton: {
        backgroundColor: '#f0f0f0',
        padding: 15,
        borderRadius: 10,
        marginVertical: 5,
        width: '80%',
    },
    selectedButton: {
        backgroundColor: '#2196F3',
    },
    preferenceText: {
        textAlign: 'center',
        fontSize: 16,
    },
});

export default google_oauth;