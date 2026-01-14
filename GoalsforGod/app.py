from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'goalsforgod_happy_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goalsforgod.db'
db = SQLAlchemy(app)

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    role = db.Column(db.String(50))
    personal_goals = db.relationship('PersonalGoal', backref='user', lazy=True)

class PersonalGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    bible_verse = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tasks = db.relationship('PersonalTask', backref='goal', lazy=True, cascade="all, delete-orphan")

class PersonalTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    is_completed = db.Column(db.Boolean, default=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('personal_goal.id'))

# --- LOGIN SETUP ---
login_manager = LoginManager(); login_manager.login_view = 'login'; login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

# --- ROUTES ---
@app.route('/')
def index():
    # If a user visits the main site, send them to login
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('personal_dashboard.html', goals=current_user.personal_goals)

@app.route('/create_personal_goal', methods=['POST'])
@login_required
def create_personal_goal():
    title = request.form.get('title').lower()
    verse = "I can do all things through Christ who strengthens me. - Phil 4:13 (NLT)"
    if "pray" in title: verse = "Pray without ceasing. - 1 Thess 5:17 (AMP)"
    elif "read" in title: verse = "Your word is a lamp to my feet. - Psalm 119:105 (NLT)"
    
    new_goal = PersonalGoal(title=request.form.get('title'), bible_verse=verse, user_id=current_user.id)
    db.session.add(new_goal)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_task/<int:goal_id>', methods=['POST'])
@login_required
def add_task(goal_id):
    new_task = PersonalTask(description=request.form.get('task'), goal_id=goal_id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = PersonalTask.query.get(task_id)
    task.is_completed = not task.is_completed
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/setup')
def setup():
    db.drop_all(); db.create_all()
    db.session.add(User(username='me', password='123', role='personal'))
    db.session.commit()
    return "Happy System Ready! Go to /login"

if __name__ == '__main__':
    app.run(debug=True)
