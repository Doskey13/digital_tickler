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
from flask import Flask, render_template, request, redirect, url_for, jsonify
from supabase import create_client, Client
import os

# Initialize Supabase Client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route('/ledger', methods=['GET'])
def view_ledger():
    # Fetch all records sorted by date descending
    response = supabase.table('account_ledger').select('*').order('transaction_date', desc=True).execute()
    records = response.data
    
    # Auto-calculate Totals
    total_credits = sum(float(r['amount']) for r in records if r['transaction_type'] == 'CREDIT' and r['status'] != 'VOIDED')
    total_debits = sum(float(r['amount']) for r in records if r['transaction_type'] == 'DEBIT' and r['status'] != 'VOIDED')
    net_balance = total_credits - total_debits
    
    return render_template('ledger.html', records=records, credits=total_credits, debits=total_debits, balance=net_balance)

@app.route('/ledger/add', methods=['POST'])
def add_ledger_entry():
    data = {
        "transaction_date": request.form.get('transaction_date'),
        "project_name_address": request.form.get('project_name_address', 'Corporate Overhead'),
        "transaction_type": request.form.get('transaction_type'), # DEBIT or CREDIT
        "category": request.form.get('category'),
        "sub_category": request.form.get('sub_category'),
        "vendor_payee": request.form.get('vendor_payee'),
        "description_notes": request.form.get('description_notes'),
        "amount": float(request.form.get('amount')),
        "payment_method": request.form.get('payment_method'),
        "reference_number": request.form.get('reference_number'),
        "status": request.form.get('status', 'CLEARED')
    }
    supabase.table('account_ledger').insert(data).execute()
    return redirect(url_for('view_ledger'))

@app.route('/ledger/update/<entry_id>', methods=['POST'])
def update_ledger_entry(entry_id):
    updated_data = {
        "transaction_date": request.form.get('transaction_date'),
        "project_name_address": request.form.get('project_name_address'),
        "transaction_type": request.form.get('transaction_type'),
        "category": request.form.get('category'),
        "vendor_payee": request.form.get('vendor_payee'),
        "description_notes": request.form.get('description_notes'),
        "amount": float(request.form.get('amount')),
        "status": request.form.get('status')
    }
    supabase.table('account_ledger').update(updated_data).eq('id', entry_id).execute()
    return redirect(url_for('view_ledger'))

@app.route('/ledger/delete/<entry_id>', methods=['POST'])
def delete_ledger_entry(entry_id):
    supabase.table('account_ledger').delete().eq('id', entry_id).execute()
    return redirect(url_for('view_ledger'))
@app.route("/delete_event/<int:id>")
def delete_event(id):
    if not is_logged_in(): return redirect(url_for("login"))
    supabase.table("schedule_events").delete().eq("id", id).execute()
    return redirect(url_for("index"))
