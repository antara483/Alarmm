# from flask import Flask, render_template, request, jsonify
# from datetime import datetime, timedelta
# import time
# import threading
# import os

# app = Flask(__name__)

# # In-memory storage for alarms and timers
# alarms = []
# timers = []
# stopwatch_start_time = None
# stopwatch_running = False
# # replace if below code doesnt work
# # def check_alarms():
# #     while True:
# #         now = datetime.now().strftime("%H:%M")
# #         for alarm in alarms[:]:
# #             if alarm['time'] == now and alarm['active']:
# #                 alarm['active'] = False
# #                 print(f"ALARM! {alarm['time']} - {alarm['label']}")
# #         time.sleep(30)
# @app.route('/api/alarm/check')
# def check_alarms():
#     now = datetime.now().strftime("%H:%M")
#     for alarm in alarms:
#         if alarm['time'] == now and alarm['active']:
#             alarm['active'] = False
#             return jsonify({
#                 'triggered': True,
#                 'time': alarm['time'],
#                 'label': alarm['label'],
#                 'id': alarms.index(alarm)
#             })
#     return jsonify({'triggered': False})

# @app.route('/api/alarm/dismiss/<int:alarm_id>')
# def dismiss_alarm(alarm_id):
#     if 0 <= alarm_id < len(alarms):
#         alarms[alarm_id]['active'] = False
#     return jsonify({'status': 'success'})

# # Start the alarm checking thread
# alarm_thread = threading.Thread(target=check_alarms, daemon=True)
# alarm_thread.start()

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
#             'remaining': total_seconds,
#             'active': True
#         })
#     return render_template('timer.html', timers=timers)

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

# if __name__ == '__main__':
#     app.run(debug=True)


import pytz
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import time
from apscheduler.schedulers.background import BackgroundScheduler

# app = Flask(__name__)
# In app.py, ensure you have:
app = Flask(__name__, static_folder='static')
# Initialize scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

# In-memory storage
alarms = []
timers = []
stopwatch_start_time = None
stopwatch_running = False

def check_alarms():
    with app.app_context():
        now = datetime.now().strftime("%H:%M")
        for alarm in alarms[:]:
            if alarm['time'] == now and alarm['active']:
                alarm['active'] = False
                print(f"ALARM! {alarm['time']} - {alarm['label']}")

# Schedule alarm checks every 30 seconds
scheduler.add_job(check_alarms, 'interval', seconds=30)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alarm', methods=['GET', 'POST'])
def alarm():
    if request.method == 'POST':
        alarm_time = request.form.get('alarm_time')
        label = request.form.get('label', 'Alarm')
        alarms.append({
            'time': alarm_time,
            'label': label,
            'active': True
        })
    return render_template('alarm.html', alarms=alarms)

@app.route('/stopwatch')
def stopwatch():
    return render_template('stopwatch.html')

@app.route('/timer', methods=['GET', 'POST'])
def timer():
    if request.method == 'POST':
        hours = int(request.form.get('hours', 0))
        minutes = int(request.form.get('minutes', 0))
        seconds = int(request.form.get('seconds', 0))
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        end_time = datetime.now() + timedelta(seconds=total_seconds)
        
        timers.append({
            'end_time': end_time.strftime("%Y-%m-%d %H:%M:%S"),
            'initial': total_seconds,
            'remaining': total_seconds,
            'active': True
        })
    return render_template('timer.html', timers=timers)

# API Endpoints
@app.route('/api/alarm/check')
def api_check_alarms():
    now = datetime.now().strftime("%H:%M")
    triggered_alarms = [alarm for alarm in alarms if alarm['time'] == now and alarm['active']]
    for alarm in triggered_alarms:
        alarm['active'] = False
    return jsonify({'triggered': bool(triggered_alarms), 'alarms': triggered_alarms})

@app.route('/api/alarm/dismiss/<int:alarm_id>', methods=['POST'])
def dismiss_alarm(alarm_id):
    if 0 <= alarm_id < len(alarms):
        alarms[alarm_id]['active'] = False
    return jsonify({'status': 'success'})

@app.route('/api/stopwatch/start', methods=['POST'])
def start_stopwatch():
    global stopwatch_start_time, stopwatch_running
    if not stopwatch_running:
        stopwatch_start_time = time.time()
        stopwatch_running = True
    return jsonify(success=True)

@app.route('/api/stopwatch/stop', methods=['POST'])
def stop_stopwatch():
    global stopwatch_running
    stopwatch_running = False
    return jsonify(success=True)

@app.route('/api/stopwatch/reset', methods=['POST'])
def reset_stopwatch():
    global stopwatch_start_time, stopwatch_running
    stopwatch_start_time = None
    stopwatch_running = False
    return jsonify(success=True)

@app.route('/api/stopwatch/status', methods=['GET'])
def stopwatch_status():
    if stopwatch_running and stopwatch_start_time:
        elapsed = time.time() - stopwatch_start_time
        return jsonify(running=True, elapsed=elapsed)
    return jsonify(running=False, elapsed=0)

@app.route('/api/timer/status', methods=['GET'])
def timer_status():
    now = datetime.now()
    active_timers = []
    for timer in timers[:]:
        end_time = datetime.strptime(timer['end_time'], "%Y-%m-%d %H:%M:%S")
        if end_time > now:
            remaining = (end_time - now).total_seconds()
            active_timers.append({
                'end_time': timer['end_time'],
                'initial': timer['initial'],
                'remaining': remaining
            })
        else:
            timers.remove(timer)
            active_timers.append({
                'end_time': timer['end_time'],
                'remaining': 0,
                'expired': True
            })
    return jsonify(timers=active_timers)

@app.route('/api/timer/cancel', methods=['POST'])
def cancel_timer():
    timer_index = request.json.get('index')
    if 0 <= timer_index < len(timers):
        timers.pop(timer_index)
    return jsonify({'status': 'success'})
@app.route('/worldclock')
def worldclock():
    # Get all timezones
    timezones = sorted(pytz.all_timezones)
    return render_template('worldclock.html', timezones=timezones)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        scheduler.shutdown()

    