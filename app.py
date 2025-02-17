from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# User-defined modules
import modules.dbmanage as dbm
from modules.auth import verify_login

app = Flask(__name__)
app.secret_key = "secret_key_add_method_to_replace_with_env"

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User class required for Flask Login (UserMixin is helper function)
# load_user creates User object, gives session identitity kinda
class User(UserMixin):
    def __init__(self, username):
        self.id = username 
        self.role = "user"

@login_manager.user_loader
def load_user(username):
    return User(username)

# Routes
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if verify_login(username, password):
            user = load_user(username)
            login_user(user) #actuall login
            if(username == "admin"):
                user.role = "admin"
                return redirect("/admin/dashboard")
            return redirect(url_for('user_dashboard'))
        else:
            error = "Invalid username or password."

    return render_template('login`.html', error=error)

# Protected Routes
@app.route('/admin/dashboard')
@login_required  
def admin_dashboard():
    return f"Welcome, {current_user.id}! <a href='/logout'>Logout</a>"

@app.route('/user/dashboard')
@login_required  
def user_dashboard():
    return f"Welcome, {current_user.id}! <a href='/logout'>Logout</a>"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    dbm.start_checkup()
    app.run(debug=True)