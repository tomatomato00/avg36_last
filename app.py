import sqlite3
from datetime import timedelta 
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

app.secret_key = 'team3avg36'
app.permanent_session_lifetime = timedelta(minutes=45)

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
    cur = conn.cursor()

    # 入力フォームが全て埋まっているかの確認
    if last_name != "" and first_name != "" and mail != ""\
        and tel != "" and password != "" :

        cur.execute("SELECT id FROM register WHERE mail=?",(mail,))
        user_id = cur.fetchone()

        if user_id is None :
            cur.execute("insert into register values (NULL, ?, ?, ?, ?, ?)", (last_name, first_name, mail, tel, password))
            conn.commit()
            cur.close()
            
            conn = sqlite3.connect("avg36.db")
            cur = conn.cursor()
            cur.execute("SELECT id FROM register WHERE mail=?",(mail,))
            register_id = cur.fetchone()
            cur.execute("INSERT INTO members values (NULL, NULL, NULL, NULL, NULL, NULL,\
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, ?)", (register_id[0],))
            conn.commit()
            # color.dbとの接続を終了
            cur.close()
            return render_template("login.html")
        else :
            return render_template("regist_done.html")

    else :
        return render_template("regist_again.html")


# ログインページを表示
@app.route("/login", methods = ["GET"])
def login_get():
    return render_template("login.html")

# ログインで情報をやり取りする
@app.route("/login", methods = ["GET", "POST"])
def login_post():
    mail = request.form.get("mail")
    password = request.form.get("password")

    conn = sqlite3.connect("avg36.db")
    c = conn.cursor()
    # ログイン情報からregister_idを取得し、sessionに格納する
    c.execute("select id from register where mail = ? and password = ?",\
        (mail, password))
    register_id = c.fetchone()
    c.close()

    if register_id is None :
        return redirect("/form")

    else :
        session["id"] = register_id[0]
        return redirect("/editpage")

@app.route("/editpage", methods = ["GET"])
def editpage_get():
    if "id" in session :
        # sessionからuser_idを取得し、registerテーブルから名前を取ってきて表示する
        user_id = session["id"]
        conn = sqlite3.connect("avg36.db")
        cur = conn.cursor()
        cur.execute("SELECT first_name FROM register WHERE id=?",(user_id,))
        firstname = cur.fetchone()
        cur.close()

        # membersから編集前の情報を取ってくる
        conn = sqlite3.connect("avg36.db")
        cur = conn.cursor()
        cur.execute("SELECT name, img, top_free, portfolio, price_min, price_max, twitter,\
            insta, facebook, mail, tel, free FROM members WHERE register_id=?",(user_id,))
        user_list = cur.fetchall()
        user = user_list[0]
        cur.close()
        name = user[0]
        img = user[1]
        topfree = user[2]
        portfolio = user[3]
        min = user[4]
        max = user[5]
        twitter = user[6]
        insta = user[7]
        facebook = user[8]
        mail = user[9]
        tel = user[10]
        free = user[11]

        return render_template("mypage_edit.html", name = firstname[0], name_print=name, img=img,\
            top_free=topfree, portfolio=portfolio, min=min, max=max, t_url=twitter, i_url=insta,\
                f_url=facebook, mail=mail, tel=tel, free=free)
    else:
        return redirect("/login")

@app.route("/editpage", methods = ["GET", "POST"])
def editpage_post():
    if "id" in session :
        user_id = session["id"]

        # 入力フォームに入ってきた値を受けとり、DBをアップデートする
        name = request.form.get("name")
        img = request.form.get("img_url")
        manager = request.form.get("mamagement")
        topfree = request.form.get("top_free")
        portfolio = request.form.get("portfolio")
        min = request.form.get("min")
        max = request.form.get("max")
        twitter = request.form.get("t_url")
        insta = request.form.get("i_url")
        facebook = request.form.get("f_url")
        mail = request.form.get("mail")
        tel = request.form.get("tel")
        free = request.form.get("free")
        appear = request.form.get("appear")

        conn = sqlite3.connect("avg36.db")
        c = conn.cursor()
        c.execute("UPDATE members SET name=?, img=?, manager=?, top_free=?, portfolio=?, \
            price_min=?, price_max=?, twitter=?, insta=?, facebook=?, mail=?, tel=?, \
                free=?, appear=? WHERE register_id=?",(name, img, manager, topfree, \
                    portfolio, min, max, twitter, insta, facebook, mail, tel, free, appear, user_id))
        conn.commit()
        c.close()
        
        return render_template("edit_done.html")
    else:
        return redirect("/login")


# ログアウト機能
@app.route("/logout", methods = ["GET"])
def logout() :
    session.pop("id", None)
    return redirect("\login")





















# 404error
@app.errorhandler(404) # 404エラーが発生した場合の処理
def error_404(error):
    # return render_template('404.html')
    return "ここは404エラー！"


if __name__ == "__main__" :

    app.run(debug=True)
