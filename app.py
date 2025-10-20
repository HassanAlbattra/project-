from flask import Flask, request, jsonify, render_template
import uuid
from datetime import datetime
import json
import os

app = Flask(__name__)  # Flask serves /static by default from ./static

TASKS_FILE = 'data.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_tasks():
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
        print(f"Tasks saved successfully to {TASKS_FILE}")
        print(f"Current tasks count: {len(tasks)}")
    except Exception as e:
        print(f"Error saving tasks: {e}")

tasks = load_tasks()

def create_task(content):
    return {
        'id': str(uuid.uuid4()),
        'content': content,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }

# ---------- Page routes ----------
@app.route('/')
def home():
    return render_template('index.html')

# (Optional) keep if you still use the task edit page from before:
# @app.route('/update/<task_id>')
# def update_page(task_id):
#     return render_template('update.html', task_id=task_id)

# ---------- REST API ----------
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks}), 200

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        return jsonify(task), 200
    return jsonify({'error': 'Task not found'}), 404

@app.route('/tasks', methods=['POST'])
def create_new_task():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400

    task = create_task(data['content'])
    tasks.append(task)
    save_tasks()
    return jsonify(task), 201

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json() or {}
    if 'content' in data:
        task['content'] = data['content']
    if 'status' in data:
        if data['status'] not in ['pending', 'done']:
            return jsonify({'error': 'Status must be either "pending" or "done"'}), 400
        task['status'] = data['status']

    save_tasks()
    return jsonify(task), 200

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks()
    return jsonify({'message': 'Task deleted successfully'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'tasks_count': len(tasks)}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)