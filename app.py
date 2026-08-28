import os
from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret-key")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "doskey123")

# Supabase Setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Helper function to check login
def is_logged_in():
    return session.get("authenticated", False)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == APP_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("index"))
        else:
            error = "Incorrect password. Please try again."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not is_logged_in():
        return redirect(url_for("login"))

    records = supabase.table("tickler_records").select("*").execute().data
    events = supabase.table("schedule_events").select("*").execute().data

    return render_template("index.html", records=records, events=events)

# --- TICKLER ROUTES ---
@app.route("/add_tickler", methods=["POST"])
def add_tickler():
    if not is_logged_in(): return redirect(url_for("login"))
    data = {
        "client_name": request.form.get("client_name"),
        "category": request.form.get("category"),
        "gen_date": request.form.get("gen_date") or None,
        "followup_date": request.form.get("followup_date") or None,
        "phone": request.form.get("phone"),
        "email": request.form.get("email"),
        "notes": request.form.get("notes")
    }
    supabase.table("tickler_records").insert(data).execute()
    return redirect(url_for("index"))

@app.route("/edit_tickler/<int:id>", methods=["POST"])
def edit_tickler(id):
    if not is_logged_in(): return redirect(url_for("login"))
    data = {
        "client_name": request.form.get("client_name"),
        "category": request.form.get("category"),
        "gen_date": request.form.get("gen_date") or None,
        "followup_date": request.form.get("followup_date") or None,
        "phone": request.form.get("phone"),
        "email": request.form.get("email"),
        "notes": request.form.get("notes")
    }
    supabase.table("tickler_records").update(data).eq("id", id).execute()
    return redirect(url_for("index"))

@app.route("/delete_tickler/<int:id>")
def delete_tickler(id):
    if not is_logged_in(): return redirect(url_for("login"))
    supabase.table("tickler_records").delete().eq("id", id).execute()
    return redirect(url_for("index"))

# --- SCHEDULE ROUTES ---
@app.route("/add_event", methods=["POST"])
def add_event():
    if not is_logged_in(): return redirect(url_for("login"))
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    if start_time and len(start_time) == 16: start_time += ":00"
    if end_time and len(end_time) == 16: end_time += ":00"

    event_data = {
        "title": request.form.get("title"),
        "start_time": start_time,
        "end_time": end_time,
        "notes": request.form.get("notes")
    }
    supabase.table("schedule_events").insert(event_data).execute()
    return redirect(url_for("index"))

@app.route("/edit_event/<int:id>", methods=["POST"])
def edit_event(id):
    if not is_logged_in(): return redirect(url_for("login"))
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    if start_time and len(start_time) == 16: start_time += ":00"
    if end_time and len(end_time) == 16: end_time += ":00"

    event_data = {
        "title": request.form.get("title"),
        "start_time": start_time,
        "end_time": end_time,
        "notes": request.form.get("notes")
    }
    supabase.table("schedule_events").update(event_data).eq("id", id).execute()
    return redirect(url_for("index"))

@app.route("/delete_event/<int:id>")
def delete_event(id):
    if not is_logged_in(): return redirect(url_for("login"))
    supabase.table("schedule_events").delete().eq("id", id).execute()
    return redirect(url_for("index"))
