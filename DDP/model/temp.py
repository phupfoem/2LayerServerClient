from firebase import firebase
firebase = firebase.FirebaseApplication(
    "https://cnextra-f152b-default-rtdb.firebaseio.com/", None)
data = {
    'number': [1, 2, 3],
}
result = firebase.post('/', data)
print(result)
