from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import date, timedelta
import sqlite3

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, origins="*", allow_headers="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

DATABASE = "habits.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # habits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            frequency TEXT,
            created_at TEXT
        )
    """)

    # logs table - one row per day per habit
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            date TEXT
        )
    """)

    conn.commit()
    conn.close()

create_tables()

# helper - works out streak and last done for a habit
def get_habit_stats(habit_id):
    conn = get_connection()
    cursor = conn.cursor()

    # get all logs for this habit newest first
    cursor.execute("""
        SELECT date FROM logs
        WHERE habit_id = ?
        ORDER BY date DESC
    """, (habit_id,))

    logs = [row["date"] for row in cursor.fetchall()]
    conn.close()

    today = str(date.today())

    # check if done today
    done_today = today in logs

    # last done date
    last_done = logs[0] if logs else None

    # calculate streak
    streak = 0
    check_date = date.today()

    # if not done today start checking from yesterday
    if not done_today:
        check_date = date.today() - timedelta(days=1)

    for i in range(len(logs)):
        log_date = date.fromisoformat(logs[i])
        if log_date == check_date:
            streak = streak + 1
            check_date = check_date - timedelta(days=1)
        else:
            break

    return done_today, last_done, streak


# GET all habits
@app.route("/habits", methods=["GET"])
def get_habits():
    search = request.args.get("q", "")
    conn = get_connection()
    cursor = conn.cursor()

    if search:
        cursor.execute("""
            SELECT * FROM habits
            WHERE name LIKE ? OR category LIKE ?
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM habits")

    rows = cursor.fetchall()
    conn.close()

    habits = []
    for row in rows:
        done_today, last_done, streak = get_habit_stats(row["id"])
        habit = dict(row)
        habit["done_today"] = done_today
        habit["last_done"] = last_done
        habit["streak"] = streak
        habits.append(habit)

    return jsonify(habits)


# POST add a new habit
@app.route("/habits", methods=["POST"])
def add_habit():
    data = request.get_json()

    if not data.get("name") or data["name"].strip() == "":
        return jsonify({"error": "Please enter a habit name"}), 400

    today = str(date.today())

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO habits (name, category, frequency, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        data["name"],
        data.get("category", ""),
        data.get("frequency", ""),
        today
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Habit added!", "id": new_id}), 201


# PUT edit habit name
@app.route("/habits/<int:habit_id>", methods=["PUT"])
def edit_habit(habit_id):
    data = request.get_json()

    if not data.get("name") or data["name"].strip() == "":
        return jsonify({"error": "Please enter a habit name"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE habits SET name = ? WHERE id = ?
    """, (data["name"], habit_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Habit updated!", "name": data["name"]})


# DELETE a habit
@app.route("/habits/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    cursor.execute("DELETE FROM logs WHERE habit_id = ?", (habit_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Habit deleted!"})


# POST mark habit as done today
@app.route("/habits/<int:habit_id>/done", methods=["POST"])
def mark_done(habit_id):
    today = str(date.today())
    conn = get_connection()
    cursor = conn.cursor()

    # check if already done today
    cursor.execute("""
        SELECT * FROM logs WHERE habit_id = ? AND date = ?
    """, (habit_id, today))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return jsonify({"error": "Already marked today!"}), 400

    # save the log
    cursor.execute("""
        INSERT INTO logs (habit_id, date) VALUES (?, ?)
    """, (habit_id, today))
    conn.commit()
    conn.close()

    # return updated streak
    done_today, last_done, streak = get_habit_stats(habit_id)
    return jsonify({"message": "Done!", "streak": streak})


if __name__ == "__main__":
    app.run(debug=True, port=5001)