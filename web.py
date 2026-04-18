from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from datetime import datetime
import random
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests

if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入黃福恩的網站首頁</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在日期時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href=/welcome?u=福恩&d=靜宜資管&c=資訊管理導論>GET傳值</a><hr>"
    link += "<a href=/account>POST傳值</a><hr>"
    link += "<a href=/math>次方與根號計算</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<a href=/read3>讀取Firestore資料</a><hr>"
    link += "<a href=/search>搜尋老師</a><hr>"
    link += "<a href=/spider1>爬蟲課程</a><hr>"
    link += "<a href='/movie'>查詢即將上映電影</a><hr>"
    return link

@app.route("/movie", methods=["GET", "POST"])
def movie():
    db = firestore.client()

    # :point_right: 第一次進來（GET）→ 自動爬蟲
    if request.method == "GET":
        url = "http://www.atmovies.com.tw/movie/next/"
        Data = requests.get(url)
        Data.encoding = "utf-8"

        sp = BeautifulSoup(Data.text, "html.parser")
        result = sp.select(".filmListAllX li")

        for item in result:
            try:
                picture = item.find("img").get("src").strip()

                # :star: 關鍵修正：補完整網址
                if picture.startswith("/"):
                    picture = "http://www.atmovies.com.tw" + picture

                title = item.find("div", class_="filmtitle").text.strip()

                link = item.find("a").get("href")
                movie_id = link.replace("/", "").replace("movie", "")

                hyperlink = "http://www.atmovies.com.tw" + link

                show = item.find("div", class_="runtime").text
                show = show.replace("上映日期：", "").replace("片長：", "").replace("分", "")

                showDate = show[0:10]
                showLength = show[13:]

                doc = {
                    "title": title,
                    "picture": picture,
                    "hyperlink": hyperlink,
                    "showDate": showDate,
                    "showLength": showLength
                }

                db.collection("電影").document(movie_id).set(doc)

            except Exception as e:
                print("錯誤:", e)

        return render_template("movie.html", movies=None)

    # :point_right: 查詢（POST）
    else:
        keyword = request.form["MovieTitle"]

        docs = db.collection("電影").get()

        movies = []
        for doc in docs:
            data = doc.to_dict()

            if keyword in data.get("title", ""):
                movies.append(data)

        return render_template("movie.html", movies=movies)

@app.route("/spider1")
def spider1():
    from bs4 import BeautifulSoup
    import requests

    url = "https://www1.pu.edu.tw/~tcyang/course.html"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        Data = requests.get(url, headers=headers, timeout=10, verify=False)
        Data.encoding = "utf-8"
    except Exception as e:
        return f"錯誤: {e}"

    sp = BeautifulSoup(Data.text, "html.parser")

    courses = sp.select(".team-box")

    html = "<h2>課程列表</h2>"

    for c in courses:
        a_tag = c.find("a")
        title = c.find("h4")  # 課程名稱

        if a_tag:
            link = a_tag.get("href")

            # 補完整網址
            if link and not link.startswith("http"):
                link = "https://www1.pu.edu.tw/" + link

        else:
            link = ""

        name = title.text.strip() if title else "無名稱"

        # 👉 這裡就是你要的格式
        html += f"{link}<br>"
        html += f"{name}{link}<br>"
        html += f"{link}<br><br>"

    html += "<a href='/'>回首頁</a>"

    return html

@app.route("/search", methods=["GET", "POST"])
def search():
    db = firestore.client()
    results = []
    keyword = ""
    
    if request.method == "POST":
        keyword = request.form.get("keyword")
        collection_ref = db.collection("靜宜資管")
        docs = collection_ref.get()

        for doc in docs:
            user = doc.to_dict()
            if keyword in user["name"]:
                results.append({
                    "name": user["name"],
                    "lab": user["lab"]
                })

    return render_template("search.html", results=results, keyword=keyword)

@app.route("/read3")
def read3():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()
    for doc in docs:
        Result += str(doc.to_dict()) + "<br>"
    return Result

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime=str(now))

@app.route("/me")
def me():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")    
    return render_template("welcome.html", name= user, dep = d, course = c)


@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    result = None
    x = y = opt = None

    if request.method == "POST":
        try:
            x = float(request.form["x"])
            opt = request.form["opt"]
            y = float(request.form["y"])

            if opt == "∧":
                result = x ** y

            elif opt == "√":
                if x < 0:
                    result = "負數不能開根號"
                elif y == 0:
                    result = "根號次數不能為0"
                else:
                    result = x ** (1 / y)

            else:
                result = "未知運算"

        except:
            result = "輸入錯誤"

    return render_template("math.html", result=result, x=x, y=y, opt=opt)

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)

if __name__ == "__main__":
    app.run(debug=True)