from flask import Flask
from flask_cors import CORS #connect backend and frontend
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = "habits.db" #database file in SQlite

def get_connection():                 
    conn = sqlite3.connect(DATABASE) #talk to database

    conn.row_factory = sqlite3.Row
    return conn

def create_tables(): # habits table to store habit
    conn = get_connection()
    cursor = conn.cursor()

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            frequency TEXT NOT NULL,
            created_at TEXT
        )
    """)
    

    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            date TEXT
        )
    """)    #log table to store when habit is mark as done

    conn.commit()
    conn.close()

create_tables()

# test to check flask 
@app.route("/")
def home():
    return "Habit Tracker is running!"

# start flask
if __name__ == "__main__":
    app.run(debug=True)

    # this route sends all habits from database to the frontend
@app.route("/api/habits", methods=["GET"])
def get_habits():

    conn = get_connection()
    cursor = conn.cursor()

    # get everything from habits table
    cursor.execute("SELECT * FROM habits")

    # fetchall gives us all the rows
    all_habits = cursor.fetchall()

    conn.close()

    # we cant send sqlite rows directly to frontend
    # so we convert each row into a dictionary first
    habits_list = []
    for row in all_habits:
        habits_list.append(dict(row))

    # jsonify converts the list to json format
    # json is how frontend and backend talk to each other
    from flask import jsonify
    return jsonify(habits_list)

