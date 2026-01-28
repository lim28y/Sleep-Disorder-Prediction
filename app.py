from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import joblib
import numpy as np
import ollama
from datetime import datetime
from pdf_rag import ask_rag_advice 
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sleep'

# --- CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '217522', 
    'database': 'sleep_app'
}

# --- LOAD MODEL ---
try:
    model = joblib.load('model.pkl')
except:
    model = None

# --- DATABASE CONNECTION ---
def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except:
        return None

# --- HELPER: CHECK CHRONIC CONDITION (2 MONTHS) ---
def check_chronic_alert(user_id):
    conn = get_db_connection()
    if not conn: return False
    
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT prediction_result FROM weekly_summaries WHERE user_id = %s ORDER BY created_at DESC LIMIT 8"
    cursor.execute(sql, (user_id,))
    weeks = cursor.fetchall()
    conn.close()

    if len(weeks) < 8: return False 

    bad_count = 0
    for w in weeks:
        res = w['prediction_result']
        if "Insomnia" in res or "Apnea" in res:
            bad_count += 1
            
    return bad_count >= 6

@app.context_processor
def inject_alerts():
    if 'user_id' in session:
        is_chronic = check_chronic_alert(session['user_id'])
        return dict(chronic_alert=is_chronic)
    return dict(chronic_alert=False)

# --- HELPER: GET LOGS (🟢 UPDATED: Shows ALL logs, not just 7) ---
def get_all_logs(user_id):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    
    # REMOVED "LIMIT 7" so it shows everything
    sql = """
        SELECT log_date, sleep_duration, quality_sleep, stress_level, 
               activity_level, bp_systolic, bp_diastolic, heart_rate, daily_steps
        FROM user_sleep_data 
        WHERE user_id = %s 
        ORDER BY log_date DESC
    """
    cursor.execute(sql, (user_id,))
    logs = cursor.fetchall()
    conn.close()
    
    # Format data for charts/display
    for log in logs:
        log['log_date'] = str(log['log_date'])
        log['sleep_duration'] = float(log['sleep_duration'])
        log['stress_level'] = int(log['stress_level'])
        log['activity_level'] = int(log['activity_level'])
        log['heart_rate'] = int(log['heart_rate'])
        log['daily_steps'] = int(log['daily_steps'])
    return logs

# --- HELPER: CALCULATE AVERAGE ---
def calculate_weekly_average(logs):
    if not logs: return None
    # Use only the first 7 logs passed to this function
    logs = logs[:7] 
    count = len(logs)
    
    total_duration = sum(float(log['sleep_duration']) for log in logs)
    total_quality = sum(int(log['quality_sleep']) for log in logs)
    total_stress = sum(int(log['stress_level']) for log in logs)
    total_steps = sum(int(log['daily_steps']) for log in logs)
    total_heart = sum(int(log['heart_rate']) for log in logs)
    total_sys = sum(int(log['bp_systolic']) for log in logs)
    total_dia = sum(int(log['bp_diastolic']) for log in logs)
    total_activity = sum(int(log['activity_level']) for log in logs)

    latest = logs[0] 
    return {
        'gender': int(latest['gender']),
        'age': int(latest['age']),
        'bmi': int(latest['bmi_category']), 
        'duration': round(total_duration / count, 1),
        'quality': int(round(total_quality / count)),
        'stress': int(round(total_stress / count)),
        'daily_steps': int(total_steps / count),
        'heart_rate': int(total_heart / count),
        'bp_sys': int(total_sys / count),
        'bp_dia': int(total_dia / count),
        'activity': int(total_activity / count)
    }

# --- ML PREDICTION ---
def run_prediction(data):
    if model is None: return "Model Error"
    try:
        features = np.array([[
            int(data['gender']), int(data['age']), float(data['duration']),
            int(data['quality']), int(data['activity']), int(data['stress']),
            int(data['bmi']), int(data['heart_rate']), int(data['bp_sys']),
            int(data['bp_dia']), int(data['daily_steps'])        
        ]])
        pred = model.predict(features)[0]
        
        # Mapping based on your previous tests
        if pred == 0 or pred == "None" or pred == "Normal": 
            return "Normal"
        elif pred == 1 or pred == "Insomnia": 
            return "Insomnia Detected"
        elif pred == 2 or pred == "Sleep Apnea": 
            return "HIGH RISK: Sleep Apnea Detected"
        else: 
            return f"Detected: {pred}"
    except: return "Prediction Error"

# --- ROUTES ---

@app.route('/')
def home():
    if 'user_id' in session:
        conn = get_db_connection()
        last_log = None
        if conn:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT age, gender, bmi_category FROM user_sleep_data WHERE user_id = %s ORDER BY log_date DESC LIMIT 1"
            cursor.execute(sql, (session['user_id'],))
            last_log = cursor.fetchone()
            conn.close()
        return render_template('index.html', username=session['username'], defaults=last_log)
    return redirect(url_for('login'))

@app.route('/history')
def history():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # 1. Get ALL Logs (Fixed: No longer limited to 7)
        logs = get_all_logs(user_id)
        
        # 2. Get Monthly Progress
        conn = get_db_connection()
        monthly_data = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT week_start_date, avg_sleep_duration, avg_quality, avg_stress, prediction_result 
                FROM weekly_summaries 
                WHERE user_id = %s 
                ORDER BY created_at ASC 
                LIMIT 4
            """
            cursor.execute(sql, (user_id,))
            monthly_data = cursor.fetchall()
            conn.close()
            
        return render_template('history.html', 
                             username=session['username'], 
                             logs=logs, 
                             monthly_data=monthly_data)
                             
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(sql, (username, hashed_password))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except: return "Error: Username exists."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            conn.close()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/submit_log', methods=['POST'])
def submit_log():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    user_id = session['user_id']
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            # 1. Insert Daily Log
            insert_sql = """
                INSERT INTO user_sleep_data 
                (user_id, log_date, gender, age, sleep_duration, quality_sleep, 
                 activity_level, stress_level, bmi_category, bp_systolic, bp_diastolic, 
                 heart_rate, daily_steps)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (user_id, data['date'], data['gender'], data['age'], data['duration'], data['quality'], 
                      data['activity'], data['stress'], data['bmi'], data['bp_sys'], data['bp_dia'], 
                      data['heart_rate'], data['daily_steps'])
            cursor.execute(insert_sql, params)
            conn.commit()

            # 2. Daily AI Advice (Always Run)
            current_log_data = {
                'gender': data['gender'], 'age': data['age'], 'bmi': data['bmi'],
                'duration': data['duration'], 'quality': data['quality'], 'stress': data['stress'],
                'daily_steps': data['daily_steps'], 'heart_rate': data['heart_rate'],
                'bp_sys': data['bp_sys'], 'bp_dia': data['bp_dia'], 'activity': data['activity']
            }
            daily_pred = run_prediction(current_log_data)
            daily_tip = ask_rag_advice(current_log_data, daily_pred)

            response_data = {
                "daily_tip": daily_tip,
                "weekly_ready": False,
                "analysis": None
            }

            # 3. 🟢 INTELLIGENT WEEKLY CHECK (Fixes Missing Reports)
            # Count total logs
            cursor.execute("SELECT COUNT(*) as cnt FROM user_sleep_data WHERE user_id = %s", (user_id,))
            total_logs = cursor.fetchone()['cnt']
            
            # Count how many reports we SHOULD have (e.g., 15 logs = 2 reports)
            expected_reports = total_logs // 7
            
            # Count how many reports we ACTUALLY have
            cursor.execute("SELECT COUNT(*) as cnt FROM weekly_summaries WHERE user_id = %s", (user_id,))
            actual_reports = cursor.fetchone()['cnt']

            # If we are missing reports, FORCE GENERATE one now!
            if expected_reports > actual_reports and total_logs >= 7:
                print(f" Generating Missing Weekly Report... (Logs: {total_logs}, Reports: {actual_reports})")
                
                # Fetch LAST 7 days
                cursor.execute("SELECT * FROM user_sleep_data WHERE user_id = %s ORDER BY log_date DESC LIMIT 7", (user_id,))
                recent_logs = cursor.fetchall()
                
                avg_data = calculate_weekly_average(recent_logs)
                weekly_prediction = run_prediction(avg_data)

                # Save to DB
                save_sql = """
                    INSERT INTO weekly_summaries 
                    (user_id, week_start_date, avg_sleep_duration, avg_quality, avg_stress, prediction_result)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(save_sql, (
                    user_id, 
                    data['date'], 
                    avg_data['duration'], 
                    avg_data['quality'], 
                    avg_data['stress'], 
                    weekly_prediction
                ))
                conn.commit()

                response_data["weekly_ready"] = True
                response_data["analysis"] = {
                    "prediction": weekly_prediction,
                    "tips": "Weekly Summary Saved."
                }
            
            return jsonify(response_data)

        except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 500
        finally:
            conn.close()
    
    return jsonify({"error": "Database Connection Failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)