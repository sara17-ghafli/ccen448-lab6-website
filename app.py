
from flask import Flask, request, redirect, session, render_template_string
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "lab6-demo-only-change-me")

DB = "notes.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        """)

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>CCEN448 Lab 6</title>
    <style>
        body { font-family: Arial; background: #f4f6fb; padding: 40px; }
        main { max-width: 500px; margin: auto; background: white;
               padding: 30px; border-radius: 12px; }
        input, button { padding: 10px; margin: 6px 0; }
    </style>
</head>
<body>
<main>
    <h1>CCEN448 Lab 6</h1>
    {% if not logged_in %}
        <h2>Login</h2>
        <form method="post" action="/login">
            <input name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    {% else %}
        <p>Welcome, {{ username }}!</p>
        <h2>My Notes</h2>
        <form method="post" action="/add">
            <input name="content" placeholder="Write a note" required>
            <button type="submit">Save Note</button>
        </form>
        <ul>
        {% for note in notes %}
            <li>{{ note[0] }}</li>
        {% endfor %}
        </ul>
        <a href="/logout">Logout</a>
    {% endif %}
</main>
</body>
</html>
"""

@app.route("/")
def home():
    notes = []
    if session.get("logged_in"):
        with sqlite3.connect(DB) as conn:
            notes = conn.execute(
                "SELECT content FROM notes ORDER BY id DESC"
            ).fetchall()
    return render_template_string(
        PAGE,
        logged_in=session.get("logged_in"),
        username=session.get("username"),
        notes=notes
    )

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == os.environ.get("LAB_USERNAME") and password == os.environ.get("LAB_PASSWORD"):
        if not username or not password:
            return "Login is not configured", 503
        session["logged_in"] = True
        session["username"] = username
        return redirect("/")
    return "Invalid login", 401

@app.route("/add", methods=["POST"])
def add():
    if not session.get("logged_in"):
        return redirect("/")
    content = request.form.get("content", "").strip()
    if content:
        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)
