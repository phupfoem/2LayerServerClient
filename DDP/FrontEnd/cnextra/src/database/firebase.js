import firebase from 'firebase'
var firebaseConfig = {
    apiKey: "AIzaSyB3xGBHTe8xIk1SRUCMPKatHtEmSuF6efM",
    authDomain: "cnextra-f152b.firebaseapp.com",
    databaseURL: "https://cnextra-f152b-default-rtdb.firebaseio.com",
    projectId: "cnextra-f152b",
    storageBucket: "cnextra-f152b.appspot.com",
    messagingSenderId: "910626104594",
    appId: "1:910626104594:web:8df843d26e4ac9a6047fcb",
    measurementId: "G-0KRV5JV6LB"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
firebase.analytics();
export default firebase