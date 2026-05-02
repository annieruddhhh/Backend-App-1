from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import date, timedelta
 
app = Flask(__name__)
CORS(app)
 
# In-memory database - just a Python list
habits = [
    {"id": 1, "name": "Drink 2L water", "streak": 3, "last_done": None, "done_today": False},
    {"id": 2, "name": "Read 10 pages", "streak": 1, "last_done": None, "done_today": False}
]
next_id = 3
 
 
# GET /habits - return all habits
@app.route("/habits", methods=["GET"])
def get_habits():
    return jsonify(habits), 200
 
 
# POST /habits - add a new habit
@app.route("/habits", methods=["POST"])
def add_habit():
    global next_id
    data = request.get_json()
 
    # Validation
    if not data or "name" not in data or not data["name"].strip():
        return jsonify({"error": "Habit name is required"}), 400
 
    new_habit = {
        "id": next_id,
        "name": data["name"].strip(),
        "streak": 0,
        "last_done": None,
        "done_today": False
    }
    habits.append(new_habit)
    next_id += 1
    return jsonify(new_habit), 201
 
 
# PUT /habits/<id> - update habit name
@app.route("/habits/<int:habit_id>", methods=["PUT"])
def update_habit(habit_id):
    data = request.get_json()
 
    if not data or "name" not in data or not data["name"].strip():
        return jsonify({"error": "New name is required"}), 400
 
    for habit in habits:
        if habit["id"] == habit_id:
            habit["name"] = data["name"].strip()
            return jsonify(habit), 200
 
    return jsonify({"error": "Habit not found"}), 404
 
 
# DELETE /habits/<id> - delete a habit
@app.route("/habits/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id):
    habit_to_delete = None
 
    for habit in habits:
        if habit["id"] == habit_id:
            habit_to_delete = habit
 
    if habit_to_delete:
        habits.remove(habit_to_delete)
        return jsonify({"message": "Deleted"}), 200
 
    return jsonify({"error": "Habit not found"}), 404
 
 
# POST /habits/<id>/done - mark done today + streak logic
@app.route("/habits/<int:habit_id>/done", methods=["POST"])
def mark_done(habit_id):
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
 
    for habit in habits:
        if habit["id"] == habit_id:
            if habit["done_today"]:
                return jsonify({"error": "Already marked done today"}), 400
 
            if habit["last_done"] == yesterday:
                habit["streak"] += 1   # streak continues
            else:
                habit["streak"] = 1    # streak resets
 
            habit["last_done"] = today
            habit["done_today"] = True
            return jsonify(habit), 200
 
    return jsonify({"error": "Habit not found"}), 404
 
 
if __name__ == "__main__":
    app.run(debug=True, port=5000)