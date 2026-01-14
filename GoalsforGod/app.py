from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'goalsforgod_simple_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goalsforgod.db'
db = SQLAlchemy(app)

# --- MODELS ---
class Campus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    goals = db.relationship('Goal', backref='campus', lazy=True)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200)) # e.g., "Launch 144 DG Leaders"
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'))
    tasks = db.relationship('Task', backref='goal', lazy=True, cascade="all, delete-orphan")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    role = db.Column(db.String(50)) # super_admin, campus_pastor, personal
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'))
    personal_goals = db.relationship('PersonalGoal', backref='user', lazy=True)

class PersonalGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    bible_verse = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tasks = db.relationship('PersonalTask', backref='goal', lazy=True, cascade="all, delete-orphan")

class Task(db.Model): # For Campus Goals
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    is_completed = db.Column(db.Boolean, default=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'))

class PersonalTask(db.Model): # For Personal Goals
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    is_completed = db.Column(db.Boolean, default=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('personal_goal.id'))

# --- LOGIN SETUP ---
login_manager = LoginManager(); login_manager.login_view = 'login'; login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

# --- ROUTES ---
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'super_admin':
        campuses = Campus.query.all()
        return render_template('global_dashboard.html', campuses=campuses)
    elif current_user.role == 'personal':
        return render_template('personal_dashboard.html', goals=current_user.personal_goals)
    campus = Campus.query.get(current_user.campus_id)
    return render_template('campus_dashboard.html', campus=campus)

@app.route('/toggle_task/<type>/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(type, task_id):
    task = PersonalTask.query.get(task_id) if type == 'personal' else Task.query.get(task_id)
    task.is_completed = not task.is_completed
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_task/<type>/<int:goal_id>', methods=['POST'])
@login_required
def add_task(type, goal_id):
    desc = request.form.get('task')
    new_task = PersonalTask(description=desc, goal_id=goal_id) if type == 'personal' else Task(description=desc, goal_id=goal_id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/setup')
def setup():
    db.drop_all(); db.create_all()
    db.session.add(User(username='lex', password='123', role='super_admin'))
    db.session.add(User(username='me', password='123', role='personal'))
    db.session.commit()
    return "Simplified System Ready!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')