
# import pytz
# from flask import Flask, render_template, request, jsonify
# from datetime import datetime, timedelta
# import time
# from apscheduler.schedulers.background import BackgroundScheduler

# # app = Flask(__name__)
# # In app.py, ensure you have:
# app = Flask(__name__, static_folder='static')
# # Initialize scheduler
# scheduler = BackgroundScheduler(daemon=True)
# scheduler.start()

# # In-memory storage
# alarms = []
# timers = []
# stopwatch_start_time = None
# stopwatch_running = False

# def check_alarms():
#     with app.app_context():
#         now = datetime.now().strftime("%H:%M")
#         for alarm in alarms[:]:
#             if alarm['time'] == now and alarm['active']:
#                 alarm['active'] = False
#                 print(f"ALARM! {alarm['time']} - {alarm['label']}")

# # Schedule alarm checks every 30 seconds
# scheduler.add_job(check_alarms, 'interval', seconds=30)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/alarm', methods=['GET', 'POST'])
# def alarm():
#     if request.method == 'POST':
#         alarm_time = request.form.get('alarm_time')
#         label = request.form.get('label', 'Alarm')
#         alarms.append({
#             'time': alarm_time,
#             'label': label,
#             'active': True
#         })
#     return render_template('alarm.html', alarms=alarms)

# @app.route('/stopwatch')
# def stopwatch():
#     return render_template('stopwatch.html')

# @app.route('/timer', methods=['GET', 'POST'])
# def timer():
#     if request.method == 'POST':
#         hours = int(request.form.get('hours', 0))
#         minutes = int(request.form.get('minutes', 0))
#         seconds = int(request.form.get('seconds', 0))
        
#         total_seconds = hours * 3600 + minutes * 60 + seconds
#         end_time = datetime.now() + timedelta(seconds=total_seconds)
        
#         timers.append({
#             'end_time': end_time.strftime("%Y-%m-%d %H:%M:%S"),
#             'initial': total_seconds,
#             'remaining': total_seconds,
#             'active': True
#         })
#     return render_template('timer.html', timers=timers)

# # API Endpoints
# @app.route('/api/alarm/check')
# def api_check_alarms():
#     now = datetime.now().strftime("%H:%M")
#     triggered_alarms = [alarm for alarm in alarms if alarm['time'] == now and alarm['active']]
#     for alarm in triggered_alarms:
#         alarm['active'] = False
#     return jsonify({'triggered': bool(triggered_alarms), 'alarms': triggered_alarms})

# @app.route('/api/alarm/dismiss/<int:alarm_id>', methods=['POST'])
# def dismiss_alarm(alarm_id):
#     if 0 <= alarm_id < len(alarms):
#         alarms[alarm_id]['active'] = False
#     return jsonify({'status': 'success'})

# @app.route('/api/stopwatch/start', methods=['POST'])
# def start_stopwatch():
#     global stopwatch_start_time, stopwatch_running
#     if not stopwatch_running:
#         stopwatch_start_time = time.time()
#         stopwatch_running = True
#     return jsonify(success=True)

# @app.route('/api/stopwatch/stop', methods=['POST'])
# def stop_stopwatch():
#     global stopwatch_running
#     stopwatch_running = False
#     return jsonify(success=True)

# @app.route('/api/stopwatch/reset', methods=['POST'])
# def reset_stopwatch():
#     global stopwatch_start_time, stopwatch_running
#     stopwatch_start_time = None
#     stopwatch_running = False
#     return jsonify(success=True)

# @app.route('/api/stopwatch/status', methods=['GET'])
# def stopwatch_status():
#     if stopwatch_running and stopwatch_start_time:
#         elapsed = time.time() - stopwatch_start_time
#         return jsonify(running=True, elapsed=elapsed)
#     return jsonify(running=False, elapsed=0)

# @app.route('/api/timer/status', methods=['GET'])
# def timer_status():
#     now = datetime.now()
#     active_timers = []
#     for timer in timers[:]:
#         end_time = datetime.strptime(timer['end_time'], "%Y-%m-%d %H:%M:%S")
#         if end_time > now:
#             remaining = (end_time - now).total_seconds()
#             active_timers.append({
#                 'end_time': timer['end_time'],
#                 'initial': timer['initial'],
#                 'remaining': remaining
#             })
#         else:
#             timers.remove(timer)
#             active_timers.append({
#                 'end_time': timer['end_time'],
#                 'remaining': 0,
#                 'expired': True
#             })
#     return jsonify(timers=active_timers)

# @app.route('/api/timer/cancel', methods=['POST'])
# def cancel_timer():
#     timer_index = request.json.get('index')
#     if 0 <= timer_index < len(timers):
#         timers.pop(timer_index)
#     return jsonify({'status': 'success'})
# @app.route('/worldclock')
# def worldclock():
#     # Get all timezones
#     timezones = sorted(pytz.all_timezones)
#     return render_template('worldclock.html', timezones=timezones)

# if __name__ == '__main__':
#     try:
#         app.run(debug=True)
#     finally:
#         scheduler.shutdown()

import pytz
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
import time
from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Antara@123',
    'database': 'timemaster_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# User model
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

# User loader
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user_data:
        return User(id=user_data['id'], username=user_data['username'], email=user_data['email'])
    return None

# Create tables if they don't exist
# def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(128) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alarms (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        time VARCHAR(5) NOT NULL,
        label VARCHAR(100),
        active BOOLEAN DEFAULT TRUE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        end_time DATETIME NOT NULL,
        initial INT NOT NULL,
        remaining INT NOT NULL,
        active BOOLEAN DEFAULT TRUE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
# testing work
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # test work ori
        # Create users table
        # cursor.execute("""
        # CREATE TABLE IF NOT EXISTS users (
        #     id INT AUTO_INCREMENT PRIMARY KEY,
        #     username VARCHAR(50) UNIQUE NOT NULL,
        #     email VARCHAR(100) UNIQUE NOT NULL,
        #     password_hash VARCHAR(128) NOT NULL,
        #     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        # )
        # """)
        # test work ori

        # test
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,  # Changed from 128 to 255
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        # test

        # Create alarms table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alarms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            time VARCHAR(5) NOT NULL,
            label VARCHAR(100),
            active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        
        # Create timers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS timers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            end_time DATETIME NOT NULL,
            initial INT NOT NULL,
            remaining INT NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        
        conn.commit()
    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
# test working
# Call the initialization function
initialize_database()

# In-memory storage (for non-persistent features)
stopwatch_start_time = None
stopwatch_running = False
# alarm cancel check
def check_alarms():
    with app.app_context():
        now = datetime.now().strftime("%H:%M")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get active alarms that match current time
        cursor.execute("SELECT * FROM alarms WHERE time = %s AND active = TRUE", (now,))
        triggered_alarms = cursor.fetchall()
        
        for alarm in triggered_alarms:
            # Mark alarm as inactive
            cursor.execute("UPDATE alarms SET active = FALSE WHERE id = %s", (alarm['id'],))
            print(f"ALARM! {alarm['time']} - {alarm.get('label', 'Alarm')}")
        
        conn.commit()
        cursor.close()
        conn.close()

# allarm cancel ori

# test above
# @app.route('/api/alarm/check')
# @login_required
# def api_check_alarms():
#     now = datetime.now().strftime("%H:%M")
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
    
#     cursor.execute("SELECT * FROM alarms WHERE user_id = %s AND time = %s AND active = TRUE", (current_user.id, now))
#     triggered_alarms = cursor.fetchall()

#     # Deactivate alarms that have been triggered
#     for alarm in triggered_alarms:
#         cursor.execute("UPDATE alarms SET active = FALSE WHERE id = %s", (alarm['id'],))
    
#     conn.commit()
#     cursor.close()
#     conn.close()

#     return jsonify({'triggered': bool(triggered_alarms), 'alarms': triggered_alarms})

# test above

# Schedule alarm checks every 30 seconds
scheduler.add_job(check_alarms, 'interval', seconds=30)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(id=user_data['id'], username=user_data['username'], email=user_data['email'])
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')
# test ori
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('signup'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError as e:
            conn.rollback()
            if 'username' in str(e):
                flash('Username already exists', 'danger')
            elif 'email' in str(e):
                flash('Email already exists', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('signup.html')
# test ori/


# test
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('signup'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Generate password hash with method that produces consistent length
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError as e:
            conn.rollback()
            if 'username' in str(e):
                flash('Username already exists', 'danger')
            elif 'email' in str(e):
                flash('Email already exists', 'danger')
        except Exception as e:
            conn.rollback()
            flash('An error occurred during registration', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('signup.html')
# test

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))
# alarm cancel button ori
@app.route('/alarm', methods=['GET', 'POST'])
@login_required
def alarm():
    if request.method == 'POST':
        alarm_time = request.form.get('alarm_time')
        label = request.form.get('label', 'Alarm')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alarms (user_id, time, label) VALUES (%s, %s, %s)",
            (current_user.id, alarm_time, label)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Alarm set successfully!', 'success')
    
    # Get user's alarms
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alarms WHERE user_id = %s", (current_user.id,))
    alarms = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('alarm.html', alarms=alarms)
# alarm cancel button ori
# test above
# @app.route('/alarm', methods=['GET', 'POST'])
# @login_required
# def alarm():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
    
#     if request.method == 'POST':
#         alarm_time = request.form.get('alarm_time')
#         label = request.form.get('label', 'Alarm')
#         cursor.execute(
#             "INSERT INTO alarms (user_id, time, label, active) VALUES (%s, %s, %s, TRUE)",
#             (current_user.id, alarm_time, label)
#         )
#         conn.commit()
#         flash("Alarm set successfully!", "success")
#         return redirect(url_for('alarm'))

#     # Fetch current user's alarms
#     cursor.execute("SELECT * FROM alarms WHERE user_id = %s ORDER BY time", (current_user.id,))
#     alarms = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('alarm.html', alarms=alarms)

# test above

@app.route('/stopwatch')
@login_required
def stopwatch():
    return render_template('stopwatch.html')

@app.route('/timer', methods=['GET', 'POST'])
@login_required
def timer():
    if request.method == 'POST':
        hours = int(request.form.get('hours', 0))
        minutes = int(request.form.get('minutes', 0))
        seconds = int(request.form.get('seconds', 0))
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        end_time = datetime.now() + timedelta(seconds=total_seconds)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO timers (user_id, end_time, initial, remaining) VALUES (%s, %s, %s, %s)",
            (current_user.id, end_time.strftime("%Y-%m-%d %H:%M:%S"), total_seconds, total_seconds)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Timer started!', 'success')
    
    # Get user's timers
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM timers WHERE user_id = %s", (current_user.id,))
    timers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('timer.html', timers=timers)

# API Endpoints
@app.route('/api/alarm/check')
def api_check_alarms():
    now = datetime.now().strftime("%H:%M")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM alarms WHERE time = %s AND active = TRUE", (now,))
    triggered_alarms = cursor.fetchall()
    
    for alarm in triggered_alarms:
        cursor.execute("UPDATE alarms SET active = FALSE WHERE id = %s", (alarm['id'],))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'triggered': bool(triggered_alarms), 'alarms': triggered_alarms})

@app.route('/api/alarm/dismiss/<int:alarm_id>', methods=['POST'])
@login_required
def dismiss_alarm(alarm_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE alarms SET active = FALSE WHERE id = %s AND user_id = %s", (alarm_id, current_user.id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/stopwatch/start', methods=['POST'])
@login_required
def start_stopwatch():
    global stopwatch_start_time, stopwatch_running
    if not stopwatch_running:
        stopwatch_start_time = time.time()
        stopwatch_running = True
    return jsonify(success=True)

@app.route('/api/stopwatch/stop', methods=['POST'])
@login_required
def stop_stopwatch():
    global stopwatch_running
    stopwatch_running = False
    return jsonify(success=True)

@app.route('/api/stopwatch/reset', methods=['POST'])
@login_required
def reset_stopwatch():
    global stopwatch_start_time, stopwatch_running
    stopwatch_start_time = None
    stopwatch_running = False
    return jsonify(success=True)

@app.route('/api/stopwatch/status', methods=['GET'])
@login_required
def stopwatch_status():
    if stopwatch_running and stopwatch_start_time:
        elapsed = time.time() - stopwatch_start_time
        return jsonify(running=True, elapsed=elapsed)
    return jsonify(running=False, elapsed=0)
# try ori
# @app.route('/api/timer/status', methods=['GET'])
# @login_required
# def timer_status():
#     now = datetime.now()
#     active_timers = []
    
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM timers WHERE user_id = %s", (current_user.id,))
#     user_timers = cursor.fetchall()
#     cursor.close()
#     conn.close()
    
#     for timer in user_timers:
#         end_time = datetime.strptime(timer['end_time'], "%Y-%m-%d %H:%M:%S")
#         if end_time > now:
#             remaining = (end_time - now).total_seconds()
#             active_timers.append({
#                 'id': timer['id'],
#                 'end_time': timer['end_time'],
#                 'initial': timer['initial'],
#                 'remaining': remaining
#             })
#         else:
#             active_timers.append({
#                 'id': timer['id'],
#                 'end_time': timer['end_time'],
#                 'remaining': 0,
#                 'expired': True
#             })
    
#     return jsonify(timers=active_timers)
# try ori

# test ori
@app.route('/api/timer/status', methods=['GET'])
@login_required
def timer_status():
    try:
        now = datetime.now()
        active_timers = []
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM timers WHERE user_id = %s", (current_user.id,))
        user_timers = cursor.fetchall()
        cursor.close()
        conn.close()

        for timer in user_timers:
            # Check if end_time is already a datetime object or needs parsing
            if isinstance(timer['end_time'], str):
                end_time = datetime.strptime(timer['end_time'], "%Y-%m-%d %H:%M:%S")
            else:
                end_time = timer['end_time']
                
            if end_time > now:
                remaining = (end_time - now).total_seconds()
                active_timers.append({
                    'id': timer['id'],
                    'end_time': end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'initial': timer['initial'],
                    'remaining': remaining
                })
            else:
                active_timers.append({
                    'id': timer['id'],
                    'end_time': end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'remaining': 0,
                    'expired': True
                })

        return jsonify({
            'success': True,
            'timers': active_timers
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# test ori
# cancel timer ori
# sound
# @app.route('/api/timer/cancel', methods=['POST'])
# @login_required
# def cancel_timer():
    timer_id = request.json.get('id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM timers WHERE id = %s AND user_id = %s", (timer_id, current_user.id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})
# sound
# cancel time ori

# sound test
@app.route('/api/timer/cancel', methods=['POST'])
@login_required
def cancel_timer():
    try:
        timer_id = request.json.get('id')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if this timer is expired (playing alarm)
        cursor.execute("SELECT * FROM timers WHERE id = %s AND user_id = %s", 
                      (timer_id, current_user.id))
        timer = cursor.fetchone()
        
        if timer:
            # Delete the timer
            cursor.execute("DELETE FROM timers WHERE id = %s AND user_id = %s", 
                         (timer_id, current_user.id))
            conn.commit()
            
            # If timer was expired, we should return a flag to stop the alarm
            end_time = timer[2]  # Assuming end_time is at index 2
            now = datetime.now()
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            
            if end_time <= now:
                return jsonify({
                    'status': 'success',
                    'was_playing_alarm': True
                })
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
# sound test
# new
@app.route('/api/timer/stop', methods=['POST'])
@login_required
def stop_timer():
    try:
        timer_id = request.json.get('id')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mark timer as inactive
        cursor.execute(
            "UPDATE timers SET active = FALSE WHERE id = %s AND user_id = %s",
            (timer_id, current_user.id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
# new


@app.route('/worldclock')
@login_required
def worldclock():
    timezones = sorted(pytz.all_timezones)
    return render_template('worldclock.html', timezones=timezones)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        scheduler.shutdown()   