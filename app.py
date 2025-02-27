from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
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
    def __init__(self, username,role):
        self.id = username 
        self.role = role

@login_manager.user_loader
def load_user(username):
    role = dbm.get_role(username)
    return User(username,role)

# Routes
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        valid = verify_login(username, password)
        if valid[0]:
            user = load_user(username)
            login_user(user) #actuall login
            if (user.role == "admin"):
                return redirect("/admin/dashboard")
            return redirect(url_for('user_dashboard'))
        else:
            if(valid[1] == "usr"):
                error = "Username does not exist"
            else:
                error = "Wrong Password."

    return render_template('login.html', error=error)

@app.route("/register",methods=["POST","GET"])
def register():
    message = None
    if request.method == "POST":
        user_data = []
        # AJAX with json for admin
        if request.content_type == 'application/json':
            data = request.json
            user_data = [
                data.get('username'),
                data.get('password'),
                data.get('fullname'),
                data.get('qualification'),
                data.get('dob')
            ]
            status = dbm.add_user(user_data)
            return jsonify({"status": status})

        # POST response
        user_data.append(request.form.get('username'))
        user_data.append(request.form.get('password'))
        user_data = [
            request.form.get('username'),
            request.form.get('password'),
            request.form.get('fullname'),
            request.form.get('qualification'),
            request.form.get('dob')
        ]
        status = dbm.add_user(user_data)
        if(status):
            flash("User added sucessfully","info")
            return redirect("/login")
        else:
            message="User already exists."
            render_template("register.html",message=message)
    return render_template("register.html",message=message)

# Protected Routes
@app.route('/admin')
@app.route('/admin/dashboard')
@login_required  
def admin_dashboard():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin_dashboard.html")

@app.route('/user/dashboard')
@login_required  
def user_dashboard():
    return render_template("user_dashboard.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout successful.","info")
    return redirect("/login")

if __name__ == '__main__':
    dbm.start_checkup()
    app.run(debug=True)