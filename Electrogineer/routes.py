import os
from Electrogineer import app
from flask import render_template, request, url_for, redirect, session, flash
from pymongo import MongoClient
from flask_bcrypt import bcrypt
from dotenv import load_dotenv


load_dotenv()
app.secret_key = "finesse"
client = MongoClient(os.environ.get("MONGODB_URI"))
# "ParagonDB" is the database name in MongoDb
db = client.ParagonDB
# "Data" is the collection name in ParagonDB
data_collected = db.Data


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if "email" in session:
        return redirect(url_for("signup.html"))

    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")

        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        user_found = data_collected.find_one({"username": username})
        email_found = data_collected.find_one({"email": email})

        if user_found:
            flash("Username Is Taken", "info")
            return render_template('signup.html')

        if email_found:
            flash("Email Exists", "info")
            return render_template('signup.html')

        if password != confirm_password:
            flash("Passwords Must Match", "danger")
            return render_template('signup.html')

        else:
            hashed = bcrypt.hashpw(confirm_password.encode('utf-8'), bcrypt.gensalt())
            user_input = {'username': username, 'email': email, 'password': hashed}
            data_collected.insert_one(user_input)

            user_data = data_collected.find_one({"email": email})
            new_email = user_data['email']
            username_val = user_input["username"]

            session["username"] = username_val

            flash("Signup Successful", "info")
            return render_template('index.html', email=new_email)
    return render_template('signup.html')


@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        username_found = data_collected.find_one({"username": username})
        if username_found:
            username_val = username_found['username']
            passwordcheck = username_found['password']

            # If password is correct
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                
                session["username"] = username_val
                
                flash("Login Successful", "info")
                return redirect(url_for('index'))

            else:
                flash("Incorrect Password", "danger")
                return render_template('login.html')
        else:
            flash("Username Was Not Found", "danger")
            return render_template('login.html')
    return render_template('login.html')



@app.route("/logout", methods=["POST", "GET"])
def logout():

    # If user is currently logged in
    if "username" in session:
        session.pop("username", None)
        flash("Logout Successful", "info")
    return render_template("index.html")
