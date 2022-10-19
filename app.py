import sqlite3, random
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)


# 入力フォームを表示
@app.route("/add", methods = ["GET"])
def add_get():
    if "user_id" in session :
        return render_template("add.html")
    else :
        return redirect("/login")

# 入力したタスクをDBに追加する処理
@app.route("/add", methods = ["POST"])
def add_post() :
    if "user_id" in session :
        user_id = session["user_id"]
    # 入力フォームに入ってきた値を受け取る
        task = request.form.get("task")

        conn = sqlite3.connect("tasks.db")

        # sqliteで接続したものを操作する,ということを変数に代入
        c = conn.cursor()

        # ()内のSQL文を実行してね
        # バインド変数
        c.execute("INSERT INTO tasks VALUES(NULL, ?, ?) ;", (task, user_id))

        # DBに追加するので、変更内容を保存する
        conn.commit()

        # color.dbとの接続を終了
        c.close()
        return redirect("/list")
    else :
        return redirect("/login")