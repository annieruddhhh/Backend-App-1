# Backend-App-1
# Backend - HabitFlow

## About

This is the backend of HabitFlow built using Flask. It stores habits in memory and provides APIs to manage them.

---

## Features

* Get all habits
* Add new habit
* Update habit name
* Delete habit
* Mark habit as done and track streak

---

## Tech Used

* Python
* Flask

---

## How to Run

1. Go to backend folder
2. Run:

```bash
python app.py
```

Server will run on:

```bash
http://127.0.0.1:5001
```

---

## API Endpoints

### GET /habits

Returns all habits

---

### POST /habits

Adds a new habit

---

### PUT /habits/<id>

Updates habit name

---

### DELETE /habits/<id>

Deletes a habit

---

### POST /habits/<id>/done

Marks habit as done and updates streak

---

## Note

* Data is stored in memory (not saved permanently)
* When server restarts, data will reset

---

## Important

Make sure backend is running before opening frontend, otherwise habits will not load.

