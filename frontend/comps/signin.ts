// import statusCodes along with GoogleSignin
import {
    GoogleSignin,
    statusCodes,
    isErrorWithCode,
} from '@react-native-google-signin/google-signin';
  
  // Somewhere in your code
export const signIn = async () => {
    try {
        await GoogleSignin.hasPlayServices();
        const userInfo = await GoogleSignin.signIn();
        console.log(userInfo)
    } catch (error:any) {
        if (isErrorWithCode(error)) {
        switch (error.code) {
            case statusCodes.IN_PROGRESS:
                console.log("something went wrong");
                break;
            default:
            // some other error happened
        }
        } else {
        // an error that's not related to google sign in occurred
        }
    }   
};  