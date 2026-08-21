import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client

app = Flask(__name__)

# Secret key for session signing
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-tickler-key")

# App Password
APP_PASSWORD = os.environ.get("APP_PASSWORD", "password123")

# Supabase Credentials with sanitization
SUPABASE_URL = (os.environ.get("SUPABASE_URL") or "").strip()
SUPABASE_KEY = (os.environ.get("SUPABASE_KEY") or "").strip()

# Initialize Supabase client safely without crashing app startup
supabase: Client = None
if SUPABASE_URL.startswith("http://") or SUPABASE_URL.startswith("https://"):
    try:
        if SUPABASE_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase client initialization error: {e}")

CATEGORIES = [
    "Walking For Dollars",
    "New Lead",
    "General Follow-Up",
    "Redfin For Sale",
    "Redfin Auction Sale",
    "Wholesaler Lead",
    "Meeting Scheduled",
    "Property Walkthrough",
    "Offer Submitted",
    "Under Contract",
    "Private Money / Investor",
    "Subcontractor Outreach",
    "Estimate / Quote Sent",
    "Closed - Won / Done",
    "Closed - Dead / Dead Lead",
    "Project Active",
    "Payment Due"
]

# --- LOGIN REQUIRED DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_password = request.form.get("password")
        if user_password == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            flash("Incorrect password. Please try again.")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    records = []
    if supabase:
        try:
            response = supabase.table("tickler_records").select("*").order("id", desc=True).execute()
            records = response.data if response.data else []
        except Exception as e:
            print(f"Supabase query error: {e}")
            records = []
            
    return render_template("index.html", records=records, categories=CATEGORIES)

@app.route("/add", methods=["POST"])
@login_required
def add_record():
    data = {
        "client_name": request.form.get("client_name"),
        "category": request.form.get("category"),
        "generated_date": request.form.get("generated_date"),
        "follow_up_date": request.form.get("follow_up_date"),
        "phone": request.form.get("phone") or None,
        "email": request.form.get("email") or None,
        "notes": request.form.get("notes") or None
    }
    if supabase:
        try:
            supabase.table("tickler_records").insert(data).execute()
        except Exception as e:
            print(f"Error adding record: {e}")
            
    return redirect(url_for("index"))

@app.route("/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_record(record_id):
    if supabase:
        try:
            supabase.table("tickler_records").delete().eq("id", record_id).execute()
        except Exception as e:
            print(f"Error deleting record: {e}")
            
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
