import firebase from 'firebase/app';
import * as firebaseui from 'firebaseui';
require('firebaseui/dist/firebaseui.css');

const config = {
  apiKey: 'AIzaSyA8UJByEMcsQvfpd8ObKjsa8DjQI5j9S08',
  authDomain: 'kairos-motor.firebaseapp.com',
  databaseURL: 'https://kairos-motor.firebaseio.com',
  projectId: 'kairos-motor',
  storageBucket: 'kairos-motor.appspot.com',
  messagingSenderId: '1012785306290',
};
firebase.initializeApp(config);

export {firebase, firebaseui};
