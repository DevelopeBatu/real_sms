from flask_session import Session
from flask import Flask, request, render_template, redirect, session
import sqlite3
from sms import send

do = True

# Flask constructor
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = 'mysecretkey'

name = ""
# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods =["GET", "POST"])
def gfg():
    if request.method == "POST":

        first_name = request.form.get("fname")
        # getting input with name = lname in HTML form
        last_name = request.form.get("lname")
        name = first_name
        return iki(first_name,last_name)
    return render_template("index.html",do=do)

@app.route("/register", methods =["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("fname")
        # getting input with name = lname in HTML form
        password = request.form.get("lname")
        a_password = request.form.get("aname")
        vt = sqlite3.connect('user_dene.db')
        im = vt.cursor()
        im.execute(f"SELECT * from users WHERE user_name = '{username}'")
        veriler = im.fetchall()
        if password == a_password and len(veriler)==0:
            im.execute(f"INSERT INTO users VALUES ('{username}','{password}','normal',0)")
            vt.commit()
            print("oldu")
            return render_template("go_login.html")
        else:
            do = False
            return render_template("register.html", do=False)

    return render_template("register.html",do=True)

@app.route("/anasayfa",methods=['GET', 'POST'])
def ana():
    if 'username' in session:  # Kullanıcı oturumu kontrolü
        if request.method == 'POST':
            phone_number = request.form['phone_number']
            username = session.get("username")  # Oturumdaki kullanıcı adını al

            vt = sqlite3.connect('user_dene.db')
            im = vt.cursor()
            im.execute(f"SELECT * FROM users WHERE user_name = ?", (username,))
            user_data = im.fetchone()
            if user_data:  # Kullanıcı verisi bulunduysa
                balance = user_data[3]  # Kullanıcının bakiyesini al
                new_balance = int(balance) - 10  # Bakiyeden düşüş yap
                im.execute("UPDATE users SET balance = ? WHERE user_name = ?", (new_balance, username))
                vt.commit()
                sonuc = send(phone_number, 100, 99)

            return render_template('anasayfa.html', phone_number=phone_number, sonuc=sonuc)
    else:
        return redirect('/')
    if not session.get("username"):
        return redirect("/")

    return render_template("anasayfa.html")
do = True
@app.route("/iki")
def iki(username,password):
    vt = sqlite3.connect('user_dene.db')
    im = vt.cursor()
    print(username)
    print(password)
    im.execute(f"SELECT * from users WHERE user_name = '{username}' and password = '{password}'")
    veriler = im.fetchall()
    print(veriler)
    if len(veriler)>=1:
        session["username"] = username
        return render_template("iki.html")
    else:
        do=False
        return render_template("index.html", do=do)

@app.route("/adminsayfa", methods =["GET", "POST"])
def admin():
    if 'username' in session:
        vt = sqlite3.connect('user_dene.db')
        im = vt.cursor()
        im.execute(f"SELECT * FROM users WHERE user_name = ?", (session['username'],))
        user_data = im.fetchone()
        if user_data and user_data[2] == 'admin':  # Kullanıcı var ve admin mi?
            im.execute(f"SELECT * FROM users")
            veriler = im.fetchall()
            return render_template("admin.html", veriler=veriler)
    return "Yetkisiz erişim!"

@app.route("/delete_user", methods=["GET", "POST"])
def delete_user():
    if 'username' in session:
        vt = sqlite3.connect('user_dene.db')
        im = vt.cursor()
        im.execute(f"SELECT * FROM users WHERE user_name = ?", (session['username'],))
        user_data = im.fetchone()
        if user_data and user_data[2] == 'admin':  # Kullanıcı var ve admin mi?
            if request.method == "GET":
                user_name = request.args.get("deleted_user")
                im.execute(f"DELETE FROM users WHERE user_name = ?", (user_name,))
                vt.commit()
                return render_template("delete_users.html")
        else:
            return "Yetkisiz erişim!"
    return redirect('/')

@app.route("/update_user", methods=["GET", "POST"])
def update_user():
    if 'username' in session:
        vt = sqlite3.connect('user_dene.db')
        im = vt.cursor()
        im.execute(f"SELECT * FROM users WHERE user_name = ?", (session['username'],))
        user_data = im.fetchone()
        if user_data and user_data[2] == 'admin':  # Kullanıcı var ve admin mi?
            if request.method == "GET":
                user_name = request.args.get("updated_user")
                im.execute(f"SELECT * FROM users WHERE user_name = ?", (user_name,))
                veriler = im.fetchall()
                return render_template("update.html", user_edit=veriler)
            elif request.method == "POST":
                user_status = request.form.get("balance")
                username = request.form.get("username")
                user_password = request.form.get("user_password")
                user_type = request.form.get("user_type")
                im.execute("UPDATE users SET password=?, user_type=?, balance=? WHERE user_name=?",
                           (user_password, user_type, user_status, username))
                vt.commit()
                return render_template("edit_go_user.html")
        else:
            return "Yetkisiz erişim!"
    return redirect('/')

@app.route("/update_save", methods=["GET", "POST"])
def update_save():
    if 'username' in session:
        vt = sqlite3.connect('user_dene.db')
        im = vt.cursor()
        im.execute(f"SELECT * FROM users WHERE user_name = ?", (session['username'],))
        user_data = im.fetchone()
        if user_data and user_data[2] == 'admin':  # Kullanıcı var ve admin mi?
            if request.method == "GET":
                return render_template("edit_go_user.html")
            elif request.method == "POST":
                user_status = request.form.get("balance")
                username = request.form.get("username")
                user_password = request.form.get("user_password")
                user_type = request.form.get("user_type")
                im.execute("UPDATE users SET password=?, user_type=?, balance=? WHERE user_name=?",
                           (user_password, user_type, user_status, username))
                vt.commit()
                return render_template("edit_go_user.html")
        else:
            return "Yetkisiz erişim!"
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)
