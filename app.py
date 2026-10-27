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
        print(f"DEBUG ERROR INSERTING TICKLER: {e}")

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
        print(f"DEBUG ERROR INSERTING EVENT: {e}")

    return redirect(url_for('index'))
