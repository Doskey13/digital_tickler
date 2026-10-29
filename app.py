import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    ticklers = []
    try:
        tickler_response = supabase.table("tickler_records").select("*").execute()
        ticklers = tickler_response.data or []
    except Exception as e:
        print(f"Error fetching ticklers: {e}")

    return render_template('index.html', ticklers=ticklers)

@app.route('/get_events', methods=['GET'])
def get_events():
    try:
        response = supabase.table("schedule_events").select("*").execute()
        events = response.data or []
        formatted_events = []
        for ev in events:
            formatted_events.append({
                "id": ev.get("id"),
                "title": ev.get("title"),
                "start": ev.get("start_time"),
                "end": ev.get("end_time"),
                "description": ev.get("notes")
            })
        return jsonify(formatted_events)
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return jsonify([])

@app.route('/add_tickler', methods=['POST'])
def add_tickler():
    client_name = (
        request.form.get('client_contact') or 
        request.form.get('client_name') or 
        request.form.get('name') or 
        "Unnamed Record"
    )
    category = request.form.get('category') or "General"
    follow_up_date = request.form.get('follow_up_date') or request.form.get('date') or None
    phone = request.form.get('phone') or request.form.get('phone_number') or None
    email = request.form.get('email') or None
    notes = request.form.get('notes') or request.form.get('notes_details') or None

    data = {
        "client_name": client_name,
        "category": category,
        "follow_up_date": follow_up_date,
        "phone": phone,
        "email": email,
        "notes": notes,
        "status": "Pending"
    }

    try:
        supabase.table("tickler_records").insert(data).execute()
    except Exception as e:
        print(f"DEBUG ERROR INSERTING TICKLER: {e}")

    return redirect(url_for('index'))

@app.route('/delete_tickler/<int:record_id>', methods=['POST', 'GET'])
def delete_tickler(record_id):
    try:
        supabase.table("tickler_records").delete().eq("id", record_id).execute()
    except Exception as e:
        print(f"Error deleting tickler record: {e}")
    return redirect(url_for('index'))

@app.route('/add_event', methods=['POST'])
def add_event():
    title = (
        request.form.get('title') or 
        request.form.get('task_title') or 
        request.form.get('event_title') or 
        "Untitled Event"
    )
    start_time = request.form.get('start_time') or request.form.get('start') or None
    end_time = request.form.get('end_time') or request.form.get('end') or None
    notes = request.form.get('notes') or request.form.get('event_details') or None

    if start_time and len(start_time) == 16:
        start_time += ":00-04:00"
    elif start_time and len(start_time) == 10:
        start_time += "T00:00:00-04:00"

    if end_time and len(end_time) == 16:
        end_time += ":00-04:00"
    elif end_time and len(end_time) == 10:
        end_time += "T00:00:00-04:00"

    data = {
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "notes": notes,
        "status": "Pending"
    }

    try:
        supabase.table("schedule_events").insert(data).execute()
    except Exception as e:
        print(f"DEBUG ERROR INSERTING EVENT: {e}")

    return redirect(url_for('index'))

@app.route('/delete_event/<int:event_id>', methods=['POST', 'GET'])
def delete_event(event_id):
    try:
        supabase.table("schedule_events").delete().eq("id", event_id).execute()
    except Exception as e:
        print(f"Error deleting schedule event: {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
