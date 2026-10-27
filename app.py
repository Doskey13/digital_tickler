import os
from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "workspace_secure_key")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    try:
        response = supabase.table("tickler_records").select("*").order("follow_up_date", desc=False).execute()
        ticklers = response.data if response.data else []
    except Exception as e:
        ticklers = []
    return render_template('index.html', ticklers=ticklers)

@app.route('/add_tickler', methods=['POST'])
def add_tickler():
    client_name = request.form.get('client_contact')
    category = request.form.get('category')
    follow_up_date = request.form.get('follow_up_date')
    phone = request.form.get('phone') or None
    email = request.form.get('email') or None
    notes = request.form.get('notes') or None

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
        pass

    return redirect(url_for('index'))

@app.route('/delete_tickler/<int:id>')
def delete_tickler(id):
    try:
        supabase.table("tickler_records").delete().eq("id", id).execute()
    except Exception as e:
        pass
    return redirect(url_for('index'))

@app.route('/add_event', methods=['POST'])
def add_event():
    title = request.form.get('title')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    notes = request.form.get('notes') or None

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
        pass

    return redirect(url_for('index'))

@app.route('/get_events')
def get_events():
    try:
        response = supabase.table("schedule_events").select("*").execute()
        events = response.data if response.data else []
        formatted_events = []
        for ev in events:
            formatted_events.append({
                "title": ev.get("title"),
                "start": ev.get("start_time"),
                "end": ev.get("end_time"),
                "description": ev.get("notes")
            })
        return formatted_events
    except Exception as e:
        return []

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
