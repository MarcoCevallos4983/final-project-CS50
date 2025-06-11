from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3 

# Configure the database
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
secret_key = 'secure key' #To use flash

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST": #Get the information from then user
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Must provide a username")
            return redirect("/register")
        
        if not password:
            flash("Must provide a password")
            return redirect("/register")
        
        if password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")
        
        



    else:
        return render_template("register.html")



if __name__ == "__main__":
    app.run(debug=True)

