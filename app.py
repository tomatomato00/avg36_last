from operator import methodcaller
import sqlite3
from datetime import timedelta 
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

app.secret_key = 'avg36'
app.permanent_session_lifetime = timedelta(minutes=60)

# 新規登録ページを表示
@app.route("/form", methods = ["GET"])
def regist_get():
    return render_template("regist.html")


# 登録ページで入力した情報をDBに登録し、送信する
@app.route("/form", methods = ["POST"])
def regist_post() :
    # 入力フォームに入ってきた値を受け取る
    last_name = request.form.get("last_name")
    first_name = request.form.get("first_name")
    mail = request.form.get("mail")
    tel = request.form.get("tel")
    password = request.form.get("password")

    # avg36.dbを接続する
    conn = sqlite3.connect("avg36.db")
    # sqliteで接続したものを操作する,ということを変数に代入
    c = conn.cursor()

    # 同意するにチェックが入っているかの確認
    if "agree" == False :
        return "利用規約に同意してください"

    # 入力フォームが全て埋まっているかの確認
    elif last_name != "" and first_name != "" and mail != ""\
        and tel != "" and password != "" :

        # ()内のSQL文を実行してね（バインド変数）
        c.execute("insert into register values (NULL, ?, ?, ?, ?, ?)", (last_name, first_name, mail, tel, password))

        # DBに追加するので、変更内容を保存する
        conn.commit()

        # color.dbとの接続を終了
        c.close()
        return render_template("login.html")

    else :
        return "入力フォームを全て記入してください"

# ログインページを表示
@app.route("/login", methods = ["GET"])
def login_get():
    return render_template("login.html")

# ログインで情報をやり取りする
@app.route("/login", methods = ["POST"])
def login_post():
    last_name = request.form.get("last_name")
    first_name = request.form.get("first_name")
    password = request.form.get("password")

    # avg36.dbを接続する
    conn = sqlite3.connect("avg36.db")
    # sqliteで接続したものを操作する,ということを変数に代入
    c = conn.cursor()
    # ()内のSQL文を実行してね（バインド変数）
    c.execute("select id from register where last_name = ?\
         and first_name = ? and password = ?", (last_name, first_name, password))
    
    user_id = c.fetchone()

    # color.dbとの接続を終了
    c.close()
    if user_id is None :
        return render_template("login.html")
    else:
        return (render_template("mypage_edit.html"))

# マイページ編集画面を表示する
@app.route("/editpage/<int:id>", methods = ["GET"])
def editmypage_get():
    if "user_id" in session :
        return ("/")
    else :
        return render_template("login.html")







if __name__ == "__main__" :

    app.run(debug=True)