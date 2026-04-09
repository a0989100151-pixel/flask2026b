import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 避免重複初始化
if not firebase_admin._apps:
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
    else:
        firebase_config = os.getenv('FIREBASE_CONFIG')
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

def read_firestore():
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()
    result = []
    for doc in docs:
        result.append(doc.to_dict())
    return result

# 若要整合進 Flask，在 web.py 加入以下路由：
# from read3 import read_firestore
#
# @app.route("/read3")
# def read3():
#     data = read_firestore()
#     Result = ""
#     for item in data:
#         Result += str(item) + "<br>"
#     return Result

if __name__ == "__main__":
    data = read_firestore()
    for item in data:
        print(item)