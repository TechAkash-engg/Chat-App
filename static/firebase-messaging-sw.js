importScripts('https://www.gstatic.com/firebasejs/7.16.0/firebase.js');
importScripts('https://www.gstatic.com/firebasejs/7.16.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.16.0/firebase-messaging.js');


firebase.initializeApp({
    apiKey: "AIzaSyAaKg-SQuLtvY8GVG8YVADMTXgfp4PoMkg",
    authDomain: "athrv-ed-chat-app.firebaseapp.com",
    databaseURL: "https://athrv-ed-chat-app.firebaseio.com",
    projectId: "athrv-ed-chat-app",
    storageBucket: "athrv-ed-chat-app.appspot.com",
    messagingSenderId: "441076813533",
    appId: "1:441076813533:web:904808e2cb7811b4e11534",
    measurementId: "G-8VDP2QCV0E"
});


  // Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  // Customize notification here
  const notificationTitle = 'You have new Message';
  const notificationOptions = {
    body: payload.data.message,
    click_action: 'https://athrvedchattesting.herokuapp.com/rooms/' + payload.data.click,
    icon: payload.data.icon
  };

  return self.registration.showNotification(notificationTitle,
    notificationOptions);
});
