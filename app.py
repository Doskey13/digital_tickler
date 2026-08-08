from flask import Flask, render_template_string, request, redirect, url_for
from supabase import create_client, Client
from datetime import datetime

app = Flask(__name__)

# --- SUPABASE CONNECTION ---
SUPABASE_URL = "https://nocgdusdrqtisbnbmdmk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vY2dkdXNkcnF0aXNibmJtZG1rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYxOTg3MTcsImV4cCI6MjEwMTc3NDcxN30.J1SvBrchUgtdiLvQFbJXwbtwOg6efKqsxyEyKevRfY0"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- HTML TEMPLATE ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Tickler System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 15px; background-color: #f4f6f8; color: #333; }
        h1 { color: #1a365d; font-size: 24px; text-align: center; }
        .container { max-width: 650px; margin: 0 auto; }
        .card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 15px; }
        label { font-weight: bold; font-size: 13px; color: #4a5568; margin-top: 8px; display: block; }
        input, textarea, select, button { width: 100%; padding: 10px; margin-top: 4px; box-sizing: border-box; border-radius: 5px; border: 1px solid #ccc; font-size: 15px; }
        button { background-color: #2b6cb0; color: white; font-weight: bold; border: none; cursor: pointer; margin-top: 12px; }
        button:hover { background-color: #2c5282; }
        .record { background: #fff; border-left: 5px solid #2b6cb0; margin-bottom: 12px; padding: 12px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .record h3 { margin: 0 0 5px 0; color: #2d3748; display: flex; justify-content: space-between; align-items: center;}
        .record p { margin: 4px 0; font-size: 14px; color: #4a5568; }
        .badge { background: #edf2f7; color: #2d3748; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .btn-group { display: flex; gap: 8px; margin-top: 8px; }
        .btn-complete { background-color: #38a169; }
        .btn-edit { background-color: #d69e2e; }
        .btn-cancel { background-color: #e53e3e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Digital Tickler System</h1>
        
        <!-- ADD OR EDIT RECORD FORM -->
        <div class="card">
            <h3>{% if edit_record %}✏️ Edit Record{% else %}➕ Add New Follow-Up{% endif %}</h3>
            <form action="{% if edit_record %}/update/{{ edit_record.id }}{% else %}/add{% endif %}" method="POST">
                
                <label>Client / Project Name</label>
                <input type="text" name="client_name" value="{{ edit_record.client_name if edit_record else '' }}" required>
                
                <label>Category</label>
                <select name="category">
                    <option value="General" {% if edit_record and edit_record.category == 'General' %}selected{% endif %}>General Follow-Up</option>
                    <option value="New Lead" {% if edit_record and edit_record.category == 'New Lead' %}selected{% endif %}>New Lead</option>
                    <option value="Estimate / Quote" {% if edit_record and edit_record.category == 'Estimate / Quote' %}selected{% endif %}>Estimate / Quote Sent</option>
                    <option value="Project Active" {% if edit_record and edit_record.category == 'Project Active' %}selected{% endif %}>Project Active</option>
                    <option value="Payment Due" {% if edit_record and edit_record.category == 'Payment Due' %}selected{% endif %}>Payment Due</option>
                </select>

                <div style="display: flex; gap: 10px;">
                    <div style="flex: 1;">
                        <label>Generated Date</label>
                        <input type="date" name="generated_date" value="{{ edit_record.generated_date if edit_record else today }}" required>
                    </div>
                    <div style="flex: 1;">
                        <label>Follow-Up Date</label>
                        <input type="date" name="follow_up_date" value="{{ edit_record.follow_up_date if edit_record else '' }}" required>
                    </div>
                </div>

                <div style="display: flex; gap: 10px;">
                    <div style="flex: 1;">
                        <label>Phone Number</label>
                        <input type="text" name="phone" value="{{ edit_record.phone if edit_record else '' }}">
                    </div>
                    <div style="flex: 1;">
                        <label>Email Address</label>
                        <input type="email" name="email" value="{{ edit_record.email if edit_record else '' }}">
                    </div>
                </div>

                <label>Notes / Details</label>
                <textarea name="notes" rows="2">{{ edit_record.notes if edit_record else '' }}</textarea>
                
                <button type="submit">{% if edit_record %}Save Changes{% else %}Add Record{% endif %}</button>
                {% if edit_record %}
                    <a href="/"><button type="button" class="btn-cancel">Cancel Edit</button></a>
                {% endif %}
            </form>
        </div>

        <!-- RECORD LIST -->
        <h3>Active Follow-Ups</h3>
        {% for r in records %}
        <div class="record">
            <h3>
                <span>{{ r.client_name }}</span>
                <span class="badge">{{ r.category }}</span>
            </h3>
            <p><strong>Generated Date:</strong> {{ r.generated_date }}</p>
            <p><strong>Follow-Up Date:</strong> <span style="color:#c53030; font-weight:bold;">{{ r.follow_up_date }}</span></p>
            {% if r.phone %}<p><strong>Phone:</strong> {{ r.phone }}</p>{% endif %}
            {% if r.notes %}<p><strong>Notes:</strong> {{ r.notes }}</p>{% endif %}
            
            <div class="btn-group">
                <a href="/edit/{{ r.id }}" style="flex:1;"><button type="button" class="btn-edit">Edit</button></a>
                <form action="/complete/{{ r.id }}" method="POST" style="flex:1;">
                    <button type="submit" class="btn-complete">Mark Complete</button>
                </form>
            </div>
        </div>
        {% else %}
        <p style="text-align:center; color: #718096;">No active follow-ups found.</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    response = supabase.table('tickler_records').select('*').eq('status', 'Pending').order('follow_up_date').execute()
    records = response.data
    return render_template_string(HTML_LAYOUT, records=records, today=today, edit_record=None)

@app.route('/add', methods=['POST'])
def add_record():
    data = {
        'client_name': request.form.get('client_name'),
        'category': request.form.get('category'),
        'generated_date': request.form.get('generated_date'),
        'follow_up_date': request.form.get('follow_up_date'),
        'phone': request.form.get('phone'),
        'email': request.form.get('email'),
        'notes': request.form.get('notes'),
        'status': 'Pending'
    }
    supabase.table('tickler_records').insert(data).execute()
    return redirect(url_for('index'))

@app.route('/edit/<int:record_id>')
def edit_record(record_id):
    today = datetime.now().strftime('%Y-%m-%d')
    records_res = supabase.table('tickler_records').select('*').eq('status', 'Pending').order('follow_up_date').execute()
    edit_res = supabase.table('tickler_records').select('*').eq('id', record_id).single().execute()
    return render_template_string(HTML_LAYOUT, records=records_res.data, today=today, edit_record=edit_res.data)

@app.route('/update/<int:record_id>', methods=['POST'])
def update_record(record_id):
    data = {
        'client_name': request.form.get('client_name'),
        'category': request.form.get('category'),
        'generated_date': request.form.get('generated_date'),
        'follow_up_date': request.form.get('follow_up_date'),
        'phone': request.form.get('phone'),
        'email': request.form.get('email'),
        'notes': request.form.get('notes'),
    }
    supabase.table('tickler_records').update(data).eq('id', record_id).execute()
    return redirect(url_for('index'))

@app.route('/complete/<int:record_id>', methods=['POST'])
def complete_record(record_id):
    supabase.table('tickler_records').update({'status': 'Completed'}).eq('id', record_id).execute()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)