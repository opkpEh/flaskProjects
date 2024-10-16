from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key_here"  # Change this to a random secret key
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']

        if action == 'login':
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Logged in successfully.', 'success')
                return redirect(url_for('home'))
            flash('Invalid username or password.', 'error')
        elif action == 'signup':
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'error')
            else:
                new_user = User(username=username, password=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully. Please log in.', 'success')
                return redirect(url_for('login'))

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        content = request.form['task_description']
        deadline_str = request.form['task_deadline']
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        new_task = MyTask(content=content, deadline=deadline, user_id=session['user_id'])
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error {e}")
            return f"ERROR {e}"
    else:
        tasks = MyTask.query.filter_by(user_id=session['user_id']).order_by(MyTask.created).all()
        return render_template("home.html", tasks=tasks)

@app.route("/edit_task/<int:id>", methods=["GET", "POST"])
@login_required
def edit_task(id: int):
    task = MyTask.query.get_or_404(id)
    if task.user_id != session['user_id']:
        flash('You do not have permission to edit this task.', 'error')
        return redirect(url_for('home'))
    if request.method == "POST":
        task.content = request.form['task_description']
        deadline_str = request.form['task_deadline']
        task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        task.complete = 'task_complete' in request.form
        try:
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            return f"Error: {e}"
    else:
        return render_template("edit.html", task=task)

@app.route("/delete_task/<int:id>", methods=["GET"])
@login_required
def delete_task(id):
    task = MyTask.query.get_or_404(id)
    if task.user_id != session['user_id']:
        flash('You do not have permission to delete this task.', 'error')
        return redirect(url_for('home'))
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the task: {str(e)}', 'error')
    return redirect(url_for('home'))

@app.route("/toggle_task/<int:id>", methods=["GET"])
@login_required
def toggle_task(id):
    task = MyTask.query.get_or_404(id)
    if task.user_id != session['user_id']:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    task.complete = not task.complete
    try:
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.utcnow().year}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, host="0.0.0.0", debug=True)