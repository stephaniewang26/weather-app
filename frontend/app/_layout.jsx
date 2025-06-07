import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native';

export default function RootLayout() {
  return (
    <Stack 
      screenOptions={{
        headerShown: false,
        contentStyle: {
          paddingTop: 50,
          backgroundColor: '#fff',
        },
      }}
    >
      <Stack.Screen name="(tabs)" />
    </Stack>
  );
}