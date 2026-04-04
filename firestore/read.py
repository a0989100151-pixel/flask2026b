import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firestore/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection("靜宜資管").document("Fu-En Huang")
doc = doc_ref.get()

if doc.exists:
    data = doc.to_dict()
    print("姓名:", data.get("name"))
    print("研究室:", data.get("lab"))
    print("mail:", data.get("mail"))
else:
    print("查無資料")

