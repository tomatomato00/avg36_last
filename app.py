import os
import sqlite3
import mimetypes
from datetime import timedelta 
from flask import Flask, render_template, request, redirect, session

from werkzeug.utils import secure_filename


app = Flask(__name__)

app.secret_key = 'team3avg36'
app.permanent_session_lifetime = timedelta(minutes=45)


# 画像のアップロード先のディレクトリ
app.config["UPLOAD_FOLDER"] = "./static/uploads"
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


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

        return render_template("mypage_edit.html", name = firstname[0], name_print=name, img_file=img,\
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
        img = request.form.get("img_file")
        manager = request.form.get("management")
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

        #画像アップロード
        conn = sqlite3.connect("avg36.db")

        # imgテーブルとuploadsディレクトリに,file名（数字に変換）とファイル形式を格納
        file = None
        max_title = 0
        if "img_file" in request.files :
            file = request.files["img_file"]
            type,ext = file.mimetype.split("/")
            if type != "image" :
                return "変なファイルを送らないでください"

            c = conn.cursor()
            c.execute("select max(title) from uploads")
            row = c.fetchone()
            if row[0] is None:
                max_title = 1
            else :
                max_title = int(row[0]) + 1

            file.save(os.path.join(app.config["UPLOAD_FOLDER"],f"{max_title}.{ext}"))
            
            c.execute("insert into uploads values(null, ?, ?)", (max_title, ext))
            conn.commit()
            c.execute("update members set img=? where register_id=?",(max_title, user_id))
            conn.commit()
            c.close()
            print(f"mime:{file.mimetype}\ttype={type}\ttext={ext}")


        #ポートフォリオのアップロード
        conn = sqlite3.connect("avg36.db")
        # portfolioテーブルとuploadsディレクトリに,file名（数字に変換）とファイル形式を格納
        file = None
        if "portfolio" in request.files :
            file = request.files["portfolio"]
            type,ext = file.mimetype.split("/")
            if type != "application" :
                return "変なファイルを送らないでください"

            c = conn.cursor()
            c.execute("select max(title) from uploads")
            row = c.fetchone()
            if row[0] is None:
                max_title = 1
            else :
                max_title = int(row[0]) + 1

            file.save(os.path.join(app.config["UPLOAD_FOLDER"],f"{max_title}.{ext}"))
            
            c.execute("insert into uploads values(null, ?, ?)", (max_title, ext))
            conn.commit()
            c.execute("update members set portfolio=? where register_id=?",(max_title, user_id))
            conn.commit()
            c.close()
            print(f"mime:{file.mimetype}\ttype={type}\ttext={ext}")

        return render_template("edit_done.html")
    else:
        return redirect("/login")






# TOPページの個人紹介一覧にDBからとってきた情報を表示する
@app.route("/top", methods = ["GET", "POST"])
def top_display() :
    indiv_list = []
    in_list = []
    conn = sqlite3.connect("avg36.db")
    cur = conn.cursor()
    cur.execute("SELECT name, price_min, price_max, top_free, img FROM members WHERE appear=1")
    user_list = cur.fetchall()
    for i in user_list :
        for j in i :
            in_list.append(j)
        cur.execute("SELECT filetype from uploads where title=?",(in_list[4],))
        filetype = cur.fetchone()
        in_list[4] = in_list[4] + "." + filetype[0]

        indiv_list.append(in_list)
        in_list = []
    print(indiv_list)

    # uploadsテーブルからimgのデータをとってくる
    cur.close()

    # img_file = str(img_file) + "." + filetype[0]
    return render_template("top_indiv.html", user_list=indiv_list)


# 個人詳細ページにDBからとってきた情報を表示する
@app.route("/detail", methods = ["GET", "POST"])
def indiv_detail() :
    conn = sqlite3.connect("avg36.db")
    cur = conn.cursor()
    cur.execute("SELECT name, img, portfolio, price_min, price_max, twitter, insta, facebook, mail, tel, free FROM members WHERE")
    user_list = cur.fetchall()
    i = user_list
    cur.close()
    return render_template("indiv_display.html", name=i[0], min = i[1], max = i[2], comment = i[3])





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