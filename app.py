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

# this route receives data from frontend and saves a new habit
@app.route("/api/habits", methods=["POST"])
def add_habit():

    # request.get_json() reads the data sent from frontend
    from flask import request, jsonify
    data = request.get_json()

    # basic validation - check if fields are empty
    if not data.get("name") or data["name"].strip() == "":
        return jsonify({"error": "Please enter a habit name"}), 400

    if not data.get("category") or data["category"].strip() == "":
        return jsonify({"error": "Please enter a category"}), 400

    if not data.get("frequency") or data["frequency"].strip() == "":
        return jsonify({"error": "Please enter a frequency"}), 400

    # get todays date
    from datetime import date
    today = str(date.today())

    conn = get_connection()
    cursor = conn.cursor()

    # insert the new habit into database
    # we use ? instead of putting values directly
    # this prevents sql injection attacks
    cursor.execute("""
        INSERT INTO habits (name, category, frequency, created_at)
        VALUES (?, ?, ?, ?)
    """, (data["name"], data["category"], data["frequency"], today))

    conn.commit()

    # lastrowid gives us the id of the habit we just created
    new_id = cursor.lastrowid

    conn.close()

    return jsonify({"message": "Habit added!", "id": new_id}), 201

# this route updates an existing habit
# habit_id comes from the url like /api/habits/1
@app.route("/api/habits/<int:habit_id>", methods=["PUT"])
def edit_habit(habit_id):

    from flask import request, jsonify
    data = request.get_json()

    # same validation as before
    if not data.get("name") or data["name"].strip() == "":
        return jsonify({"error": "Please enter a habit name"}), 400

    if not data.get("category") or data["category"].strip() == "":
        return jsonify({"error": "Please enter a category"}), 400

    if not data.get("frequency") or data["frequency"].strip() == "":
        return jsonify({"error": "Please enter a frequency"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # update the habit where id matches
    cursor.execute("""
        UPDATE habits
        SET name = ?, category = ?, frequency = ?
        WHERE id = ?
    """, (data["name"], data["category"], data["frequency"], habit_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Habit updated!"})

# this route deletes a habit and all its logs
@app.route("/api/habits/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id):

    from flask import jsonify
    conn = get_connection()
    cursor = conn.cursor()

    # delete the habit
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

    # also delete all logs for this habit
    # otherwise old logs stay in database with no habit attached
    cursor.execute("DELETE FROM logs WHERE habit_id = ?", (habit_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Habit deleted!"})