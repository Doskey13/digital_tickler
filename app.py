import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from supabase import create_client, Client

APP_PASSWORD = "Doskey13@"

# Supabase Credentials
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route("/")
def index():
    # Fetch tickler records
    tickler_response = supabase.table("tickler_records").select("*").execute()
    tickler_records = tickler_response.data if tickler_response else []

    # Fetch schedule events
    schedule_response = supabase.table("schedule_events").select("*").execute()
    schedule_events = schedule_response.data if schedule_response else []

    return render_template("index.html", records=tickler_records, events=schedule_events)

# --- TICKLER ROUTES ---
@app.route("/add_tickler", methods=["POST"])
def add_tickler():
    client_name = request.form.get("client_name")
    category = request.form.get("category")
    gen_date = request.form.get("gen_date")
    followup_date = request.form.get("followup_date")
    phone = request.form.get("phone")
    email = request.form.get("email")
    notes = request.form.get("notes")

    data = {
        "client_name": client_name,
        "category": category,
        "gen_date": gen_date if gen_date else None,
        "followup_date": followup_date if followup_date else None,
        "phone": phone,
        "email": email,
        "notes": notes
    }
    supabase.table("tickler_records").insert(data).execute()
    return redirect(url_for("index"))

@app.route("/delete_tickler/<int:record_id>")
def delete_tickler(record_id):
    supabase.table("tickler_records").delete().eq("id", record_id).execute()
    return redirect(url_for("index"))

# --- SCHEDULE / CALENDAR ROUTES ---
@app.route("/add_event", methods=["POST"])
def add_event():
    title = request.form.get("title")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    status = request.form.get("status", "Pending")
    notes = request.form.get("notes")

    # Format time strings to plain ISO strings without UTC conversion
    if start_time and len(start_time) == 16:
        start_time += ":00"
    if end_time and len(end_time) == 16:
        end_time += ":00"

    event_data = {
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "notes": notes
    }
    supabase.table("schedule_events").insert(event_data).execute()
    return redirect(url_for("index"))

@app.route("/delete_event/<int:event_id>")
def delete_event(event_id):
    supabase.table("schedule_events").delete().eq("id", event_id).execute()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
