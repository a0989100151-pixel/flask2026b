import firebase_admin
from firebase_admin import credentials, firestore
import requests
from bs4 import BeautifulSoup

# 🔐 初始化 Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🌐 爬蟲
url = "http://www.atmovies.com.tw/movie/next/"
Data = requests.get(url)
Data.encoding = "utf-8"

sp = BeautifulSoup(Data.text, "html.parser")

result = sp.select(".filmListAllX li")
lastUpdate = sp.find("div", class_="smaller09").text[5:]

# 📦 處理每一筆電影資料
for item in result:
    try:
        picture = item.find("img").get("src").replace(" ", "")

        # ⭐ 加這段（關鍵）
        if picture.startswith("/"):
            picture = "http://www.atmovies.com.tw" + picture
        title = item.find("div", class_="filmtitle").text.strip()

        movie_id = (
            item.find("div", class_="filmtitle")
            .find("a")
            .get("href")
            .replace("/", "")
            .replace("movie", "")
        )

        hyperlink = "http://www.atmovies.com.tw" + \
            item.find("div", class_="filmtitle").find("a").get("href")

        show = item.find("div", class_="runtime").text
        show = show.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")

        showDate = show[0:10]
        showLength = show[13:]

        # 🔥 Firestore 文件
        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate
        }

        # 📥 寫入 Firestore
        db.collection("電影").document(movie_id).set(doc)

        print(f"✅ 已寫入：{title}")

    except Exception as e:
        print(f"❌ 錯誤：{e}")

print("🎉 全部完成")