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