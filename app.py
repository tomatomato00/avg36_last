'''
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

@app.route("/login/<int:register_id>", methods = ["POST", "GET"])
def login(register_id):
  if request.method == "POST":
    session.permanent = True  
    session["id"] = register_id
    return redirect("/login")
  else:
    if "id" in session: 
      return redirect("/login")
    return render_template("/editpage/<int:register_id>") 


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
    session["id"]=

    # color.dbとの接続を終了
    c.close()
    if user_id not in session :
        return render_template("login.html")
    else:
        return redirect("/editpage/<int:register_id>"), render_template(lastname=last_name,\
            firstname=first_name, register_id=user_id)  

@app.route("/editpage/<int:register_id>", methods = ["GET"])
def editmypage_get(register_id):
    return render_template("mypage_edit.html")

# マイページを編集してデータベースに変更を加える
@app.route("/editpage/<int:register_id>", methods = ["GET", "POST"])
def editmypage(register_id):

    if "user_id" in session :
        name = request.form.get("name")
        img = request.form.get("img_url")
        management = request.form.get("management")
        portfolio = request.form.get("portfolio")
        min = request.form.get("min")
        max = request.form.get("max")
        twitter = request.form.get("t_url")
        insta = request.form.get("i_url")
        facebook = request.form.get("f_url")
        appear = request.form.get("appear")

        # avg36.dbを接続する
        conn = sqlite3.connect("avg36.db")
        c = conn.cursor()
        c.execute("SELECT register_id FROM members")
        id_list = c.fetchall()
        conn.commit()
        c.close()

        conn = sqlite3.connect("avg36.db")
        c = conn.cursor()
        if register_id in id_list :
            c.execute("UPDATE members SET name=?, img=?, price_min=?, price_max=?,\
            portfolio=?, twitter=?, insta=?, facebook=?, manager=?, appear=?, \
                WHERE register_id=?",(name, img, min, max, portfolio,\
                    twitter, insta, facebook, management, appear, register_id))
        else :
            c.execute("INSERT INTO members values (NULL, name, img, price_min, price_max\
                portfolio, twitter, insta, facebook, manager, appear, register_id)",\
                    (name, img, min, max, portfolio, twitter, insta, facebook, management, appear, register_id))

        conn.commit()
        c.close()
        return "変更を保存しました"
    else :
        return render_template("login.html")

 
'''
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
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, ?)", (register_id[0],))
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

@app.route("/editpage", methods = ["GET", "POST"])
def editpage_post():
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
        cur.execute("SELECT name, img, manager, portfolio, price_min, price_max, twitter,\
            insta, facebook, mail, tel, free, appear FROM members WHERE register_id=?",(user_id,))
        user = cur.fetchall()
        cur.close()
        return render_template("mypage_edit.html", name = firstname, name_print=user)
    else:
        return redirect("/login")

@app.route("/editpage", methods = ["GET"])
def editpage_get():
    if "id" in session :
        user = session["id"]
        user_id = user[0]



        # 入力フォームに入ってきた値を受けとる
        name = request.form.get("name")
        img = request.form.get("img_url")
        manager = request.form.get("mamagement")
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

        
        return render_template("mypage_edit.html")
    else:
        return redirect("/login")
























# 404error
@app.errorhandler(404) # 404エラーが発生した場合の処理
def error_404(error):
    # return render_template('404.html')
    return "ここは404エラー！"


if __name__ == "__main__" :

    app.run(debug=True)
