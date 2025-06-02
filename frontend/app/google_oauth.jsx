import React, { useState } from 'react'
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import { Link } from 'expo-router'; 
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
    const [message, setMessage] = useState('');

    const signIn = async () => {
        try {
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
                            preference_temperature: "neutral",
                            google_oauth_token: userInfo.data.idToken
                        }),
                    });

                    const data = await response.json();

                    if (response.ok) {
                        setMessage('User created successfully!');
                        console.log("User created:", data);
                    } else {
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
    <View>
        <Text>google_oauth</Text>
        <GoogleSigninButton
        size={GoogleSigninButton.Size.Wide}
        color={GoogleSigninButton.Color.Dark}
        onPress={signIn}
        />

        {message ? <Text>{message}</Text> : null}
    </View>
    )
}

export default google_oauth

const styles = StyleSheet.create({})