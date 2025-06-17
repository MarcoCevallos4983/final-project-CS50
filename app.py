from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3 
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import folium
import os

# Configure the database
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = 'secure key' #To use flash

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
        hash = generate_password_hash(password)

        if not username:
            flash("Must provide a username")
            return redirect("/register")
        
        if not password:
            flash("Must provide a password")
            return redirect("/register")
        
        if password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")
        
        #Create a new user in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
                       # Colocar las variables que faltan dentro del parentesis
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username already taken")
            return redirect("/register")

        return redirect("/login")
        
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST": #Get the information from then user
        #Data from the user
        username = request.form.get("username")
        password = request.form.get("password")
        
        #Validation
        if not username:
            flash("Please insert your username")
            return redirect("/login")
        if not password:
            flash("Please insert your password")
            return redirect("/login")
        
        #Query the database 
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone() #Just one user

        if row is None or not check_password_hash(row["hash"], password):
            flash("invalid username and/or password")
            return redirect("/login")
        #Remember which user has logged in
        session["user_id"] = row["id"]

        #Redirect user to principal dashboard.
        return redirect("/dashboard")

    else:
        return render_template("login.html")
    
    
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """Principal dashabord showed to users who have logged in"""
    
    if request.method == "POST":
        coorx = request.form.get("coorx")
        coory = request.form.get("coory")
        
        if coorx and coory:
            try:
                coorx = float(coorx)
                coory= float(coory)
                #Map based on the user input
                map = folium.Map(location = [coorx, coory], zoom_start=12)
                map_path = os.path.join("templates", "map.html")
                map.save(map_path)
                return render_template("dashboard.html")
            except ValueError:
                flash("Coordinates are not valid")
                return redirect("/dashboard")
        else:
            flash("Please insert coordinates")
            return redirect("/dashboard")

        
    
    else:
        #Create a map
        map = folium.Map(location = [-1.8312, -78.1834], zoom_start=7,
                        dragging=False,
                        zoom_control=False,
                        scrollWheelZoom=False,
                        doubleClickZoom=False,
                        touchZoom=False)

        #Save the map in a html file.
        map_path = os.path.join("templates", "map.html")
        map.save(map_path)

        return render_template("dashboard.html")



if __name__ == "__main__":
    app.run(debug=True)

