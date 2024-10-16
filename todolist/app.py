from flask import Flask, render_template, redirect, request, url_for
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import datetime

app = Flask(__name__)
Scss(app)

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.utcnow().year}

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.Date, nullable=True)

    def __repr__(self) -> str:
        return f"Task {self.id}"

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        content = request.form['task_description']
        deadline_str = request.form['task_deadline']
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        new_task = MyTask(content=content, deadline=deadline)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error {e}")
            return f"ERROR {e}"
    else:
        tasks = MyTask.query.order_by(MyTask.created).all()
        return render_template("home.html", tasks=tasks)

@app.route("/delete_task/<int:id>")
def delete_task(id: int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Error: {e}"

@app.route("/edit_task/<int:id>", methods=["GET", "POST"])
def edit_task(id: int):
    task = MyTask.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form['task_description']
        deadline_str = request.form['task_deadline']
        task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        try:
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            return f"Error: {e}"
    else:
        return render_template("edit.html", task=task)

@app.route("/toggle_task/<int:id>")
def toggle_task(id: int):
    task = MyTask.query.get_or_404(id)
    task.complete = not task.complete
    try:
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)