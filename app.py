from flask import Flask, request, render_template, redirect, url_for, flash
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
                error = "Usernaem does not exist"
            else:
                error = "Wrong Password."

    return render_template('login.html', error=error)

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST":
        # AJAX with json for admin
        if request.content_type == 'application/json':
            data = request.json
            username = data.get('username')
            password = data.get('password')
            dbm.add_user(username, password)
            return jsonify({"message": "Registration successful!"})

        # POST response
        username = request.form.get('username')
        password = request.form.get('password')
        dbm.add_user(username, password)
        flash("User Added Succesfully.","info")
        return redirect("/login")
    return render_template("register.html")

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