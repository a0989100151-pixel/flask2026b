import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firestore/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "黃福恩",
  "mail": "a0989100151@gmail.com",
  "lab": 801
}

doc_ref = db.collection("靜宜資管").document("Fu-En Huang")
doc_ref.set(doc)