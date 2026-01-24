from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import joblib
import numpy as np
import ollama
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sleep'

# --- CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '217522', # Check your password
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

# --- HELPER: GET LOGS (Updated to fetch ALL daily stats) ---
def get_recent_logs(user_id):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    
    # FETCH EVERYTHING except Gender, Age, BMI
    sql = """
        SELECT log_date, sleep_duration, quality_sleep, stress_level, 
               activity_level, bp_systolic, bp_diastolic, heart_rate, daily_steps
        FROM user_sleep_data 
        WHERE user_id = %s 
        ORDER BY log_date DESC 
        LIMIT 7
    """
    cursor.execute(sql, (user_id,))
    logs = cursor.fetchall()
    conn.close()
    
    # Convert Data Types for JavaScript
    for log in logs:
        log['log_date'] = str(log['log_date'])
        log['sleep_duration'] = float(log['sleep_duration'])
        # Ensure other numbers are safe
        log['stress_level'] = int(log['stress_level'])
        log['activity_level'] = int(log['activity_level'])
        log['heart_rate'] = int(log['heart_rate'])
        log['daily_steps'] = int(log['daily_steps'])
        
    return logs

# --- HELPER: AI & ML ---
# --- HELPER: SMART AI ADVICE ---
def get_ai_advice(data, prediction_result):
    if not data: return "No data available."
    
    # 1. IDENTIFY PAIN POINTS (The "Why")
    issues = []
    if float(data['duration']) < 6:
        issues.append("severe sleep deprivation")
    if int(data['stress']) > 7:
        issues.append("very high stress levels")
    if int(data['quality']) < 5:
        issues.append("poor sleep quality")
    if int(data['daily_steps']) < 3000:
        issues.append("sedentary lifestyle (low activity)")
    if int(data['bp_sys']) > 130:
        issues.append("elevated blood pressure")

    # 2. CONSTRUCT A RICH PROMPT
    # We tell the AI exactly who the user is and what is wrong.
    prompt = (
        f"Act as an empathetic medical sleep coach. "
        f"User Profile: {data['age']} year old { 'Male' if data['gender']==1 else 'Female' }. "
        f"BMI Category: { 'Overweight/Obese' if data['bmi']>0 else 'Normal' }. "
        f"Current Status: Sleep {data['duration']}h, Stress {data['stress']}/10, Steps {data['daily_steps']}. "
        f"Medical Prediction: The system predicts {prediction_result}. "
    )

    if issues:
        prompt += f"CRITICAL ISSUES TO ADDRESS: {', '.join(issues)}. "
        prompt += "Give 1 specific, actionable, and scientific tip to fix these specific issues. "
    else:
        prompt += "The user is doing well. Give 1 advanced bio-hacking tip to optimize performance further. "

    prompt += "Keep the answer short (under 2 sentences) and encouraging."

    # 3. ASK OLLAMA
    try:
        response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        print(f"AI Error: {e}")
        return "Focus on maintaining a consistent sleep schedule and reducing stress before bed."

# --- MAIN ML FUNCTION (Must match train_model.py inputs) ---
def run_prediction(data):
    if model is None: 
        print("Error: Model is not loaded.")
        return "Model Error"

    try:
        # 1. Prepare Features
        # The order must be EXACTLY: 
        # [Gender, Age, Duration, Quality, Activity, Stress, BMI, Heart Rate, Systolic, Diastolic, Steps]
        
        features = np.array([[
            int(data['gender']),      # 1=Male, 0=Female
            int(data['age']),
            float(data['duration']),
            int(data['quality']),
            int(data['activity']),
            int(data['stress']),
            int(data['bmi']),         # 0=Normal, 1=Overweight, 2=Obese
            int(data['heart_rate']),
            int(data['bp_sys']),
            int(data['bp_dia']),
            int(data['daily_steps'])        
        ]])

        # 2. Predict
        pred = model.predict(features)[0]

        # 3. Map Result
        if pred == 0: 
            return "Normal Sleep Pattern"
        elif pred == 1: 
            return "Sleep Disorder Detected (Insomnia)"
        elif pred == 2: 
            return "HIGH RISK: Sleep Apnea Detected"
        else:
            return "Unknown Result"

    except Exception as e:
        print(f"Prediction Error: {e}")
        return "Prediction Error"

# --- ROUTES ---

@app.route('/')
def home():
    if 'user_id' in session:
        # Renders the Form (Index)
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/history')
def history():
    if 'user_id' in session:
        # Renders the History Page
        logs = get_recent_logs(session['user_id'])
        return render_template('history.html', username=session['username'], logs=logs)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # If the user fills the form (POST)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 1. Hash the password (Security Best Practice)
        # Never store raw passwords!
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # 2. Insert into Database
                sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(sql, (username, hashed_password))
                conn.commit()
                conn.close()
                
                # 3. Success! Go to Login
                return redirect(url_for('login'))
                
            except mysql.connector.IntegrityError:
                # This happens if the username already exists
                return "Error: Username already exists. Please choose another."
            except Exception as e:
                return f"Registration Error: {e}"
    
    # If the user just opens the page (GET)
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
    if 'user_id' not in session: 
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    user_id = session['user_id']
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            sql = """
                INSERT INTO user_sleep_data 
                (user_id, gender, age, sleep_duration, quality_sleep, 
                 activity_level, stress_level, bmi_category, bp_systolic, bp_diastolic, 
                 heart_rate, daily_steps)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                user_id, 
                data['gender'], 
                data['age'], 
                data['duration'], 
                data['quality'], 
                data['activity'], 
                data['stress'], 
                data['bmi'], 
                data['bp_sys'], 
                data['bp_dia'], 
                data['heart_rate'], 
                data['daily_steps'] 
            )
            
            cursor.execute(sql, params)
            conn.commit()
            
            # --- THIS IS THE NEW PART ---
            
            # 1. Run Prediction (Every time, or check count % 7)
            prediction_result = run_prediction(data)
            
            # 2. Get AI Tips (assuming you have this function)
            tip = get_ai_advice(data, prediction_result)

            # 3. Return JSON
            return jsonify({
                "daily_tip": tip, 
                "weekly_ready": True,  # Set to True to see the Green Box immediately
                "analysis": {
                    "prediction": prediction_result,
                    "tips": "Consult a doctor if symptoms persist."
                }
            })

        except mysql.connector.Error as err:
            print("DB Error:", err)
            return jsonify({"error": str(err)}), 500
        finally:
            conn.close()
    
    return jsonify({"error": "Database Connection Failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)