from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# User-defined modules
import modules.dbmanage as dbm
from modules.auth import verify_login

subjects = dbm.subject()

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
# @app.route("",methods=["POST","GET"])

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
            session["user"] = valid[1]
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
        # JSON response
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
        referer = request.headers.get("Referer", "")
        user_data = [
            request.form.get('username'),
            request.form.get('password'),
            request.form.get('fullname'),
            request.form.get('qualification'),
            request.form.get('dob'),
        ]
        status = dbm.add_user(user_data)
        if(status):
            flash("User added sucessfully","info")
            if("admin" in referer):
                return redirect('/admin/dashboard')
            return redirect("/login")
        else:
            message="User already exists."
            if("admin" in referer):
                flash(message,"info")
                return redirect('/admin/dashboard')
            return render_template("register.html",message=message)
    return render_template("register.html",message=message)

@app.route('/admin')
def admin():
    return redirect("/admin/dashboard")

# Protected Routes
@app.route('/admin/dashboard')
@login_required  
def admin_dashboard():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    session["subjects"] = subjects.get()
    return render_template("admin_dashboard.html",user="Admin",sublist=session["subjects"])

@app.route("/addsubject",methods=["POST"])
@login_required
def add_subject():
    if(current_user.role != "admin"):
        return "<p>Error unauthorised</p>"
    sub_data = [
        request.form.get('code').strip(),
        request.form.get('subject').strip(),
        request.form.get('description').strip(),
    ]
    if(subjects.add(sub_data)):
        message = f"{sub_data[0]}:\"{sub_data[1]}\" added successfully"
    else:
        message = f"{sub_data[0]}:\"{sub_data[1]}\" already exists"
    flash(message,"info")
    return redirect("/admin")

@app.route("/addchapter",methods=["GET","POST"])
@login_required
def add_chapter():
    if(current_user.role != "admin"):
        return "<p>Error unauthorised</p>"
    if request.method == "POST":
        sub_data = [
            request.form.get('code').strip(),
            request.form.get('subject').strip(),
            request.form.get('description').strip(),
        ]
        if(subjects.add(sub_data)):
            return f"<p> {sub_data[0]}:\"{sub_data[1]}\" added successfully </p>"
        else:
            return f"<p> {sub_data[0]}:\"{sub_data[1]}\" already exists</p>"
    return "<p> Add Chapter interface <p>"


@app.route('/user/dashboard')
@login_required  
def user_dashboard():
    user = session["user"]
    return render_template("user_dashboard.html",user=user["fname"])

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout successful.","info")
    return redirect("/login")

if __name__ == '__main__':
    dbm.start_checkup()
    app.run(debug=True)