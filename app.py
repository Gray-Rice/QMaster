from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# User-defined modules
import modules.dbmanage as dbm
from modules.auth import verify_login

uobj = dbm.users()
sub = dbm.subject()
chap = dbm.chapter()
quiz = dbm.quiz()
qu = dbm.questions()
sc = dbm.score()

app = Flask(__name__)
app.secret_key = "secret_key_add_method_to_replace_with_env"

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User class required for Flask Login (UserMixin is helper function), load_user creates User object, gives session identitity
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
                return redirect(url_for('admin_dashboard'))
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
        user_data = [
            request.form.get('username'),
            request.form.get('password'),
            request.form.get('fullname'),
            request.form.get('qualification'),
            request.form.get('dob'),
        ]
        status = uobj.add(user_data)
        if(status):
            if request.headers.get("HX-Request"):
                return f"<p> User {user_data[0]} Added Succesfully </p>"
            flash("User added sucessfully","info")
            return redirect("/login")
        else:
            message= f"Username {user_data[0]} already exists."
            if request.headers.get("HX-Request"):
                return f"<p> {message} </p>"
            return render_template("register.html",message=message)
    return render_template("register.html",message=message)

################################################################### Protected Routes

############################################################ Admin Paths
@app.route('/admin/')
@login_required  
def admin_dashboard():
    return render_template("admin.html",user="Admin")

@app.route('/admin/users')
@login_required  
def admin_user():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin_user.html",user="Admin",userlist=uobj.get())

@app.route('/admin/subject')
@login_required  
def admin_subject():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin_subject.html",user="Admin",sublist=sub.get())

@app.route('/admin/quiz')
@login_required  
def admin_quiz():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin_quiz.html",user="Admin",sublist=sub.get())

@app.route('/admin/questions')
@login_required  
def admin_question():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin_quiz.html",user="Admin",sublist=sub.get())

############################################################ Subject paths
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
    if(sub.add(sub_data)):
        message =  f"{sub_data[0]}:\"{sub_data[1]}\" added successfully"
    else:
        message =  f"{sub_data[0]}:\"{sub_data[1]}\" already exists"
    flash(message,"info")
    return redirect(url_for("admin_subject"))

@app.route("/edit/subject", methods=["POST"])
@login_required
def edit_subject():
    up_data = [
        request.form.get("subject"),
        request.form.get("description"),
        request.form.get("sub_id")
    ]
    if(sub.update(up_data)):
        flash(f"Subject updated sucessfully","info")
    else:
        flash("Error try again","info")
    return redirect(url_for("admin_subject"))

@app.route("/delete/subject", methods=["POST"])
@login_required
def rm_subject():
    sub_id = request.form.get("sub_id")
    if(sub.remove(sub_id)):
        flash(f"Subject deleted sucessfully","info")
    else:
        flash("Error try again","info")
    return redirect(url_for("admin_subject"))

############################################################ Chapter Path
@app.route('/admin/chapter')
@login_required  
def admin_chapter():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin_chapter.html",user="Admin",sublist=sub.get())

@app.route("/addchapter",methods=["POST"])
@login_required
def add_chapter():
    if(current_user.role != "admin"):
        return "<p>Error unauthorised</p>"
    chap_data = [
        request.form.get("sub_id"),
        request.form.get('code').strip(),
        request.form.get('chapter').strip(),
        request.form.get('description').strip(),
    ]
    if(chap.add(chap_data)):
        message =  f"Chapter {chap_data[0]}:\"{chap_data[1]}\" added successfully"
    else:
        message =  f"Chapter {chap_data[0]}:\"{chap_data[1]}\" already exists"
    flash(message,"info")
    return redirect("/admin/dashboard/chapter")

@app.route("/edit/chapter", methods=["POST"])
@login_required
def edit_chapter():
    up_data = [
        request.form.get("name"),
        request.form.get("description"),
        request.form.get("chap_id")
    ]
    if(chap.update(up_data)):
        flash(f"Chapter updated sucessfully","info")
    else:
        flash("Error try again","info")
    return redirect(url_for("admin_chapter"))

@app.route("/delete/chapter", methods=["POST"])
@login_required
def del_chapter():
    chap_id = request.form.get("chap_id")
    if(chap.remove(chap_id)):
        flash(f"Chapter deleted sucessfully","info")
    else:
        flash("Error try again","info")
    return redirect(url_for("admin_chapter"))

@app.route("/get/editchap",methods=["POST"])
def get_editchap():
    sub_id = request.form.get("sub_id")
    return render_template("forms/editchap.html",chaplist=chap.get(sub_id))

@app.route("/get/delchap",methods=["POST"])
def get_delchap():
    sub_id = request.form.get("sub_id")
    return render_template("forms/delchap.html",chaplist=chap.get(sub_id))

# Quiz path
@app.route("/addquiz",methods=["POST"])
@login_required
def add_quiz():
    if(current_user.role != "admin"):
        return "<p>Error unauthorised</p>"
    quiz_data = [
        request.form.get("chap_id").strip(),
        request.form.get("name").strip(),
        request.form.get('doq'),
        request.form.get('duration'),
        request.form.get('description').strip(),
    ]
    if(quiz.add(quiz_data)):
        message =  f"\"{quiz_data[1]}\" added successfully"
    else:
        message =  f"\"{quiz_data[1]}\" already exists"
    flash(message,"info")
    return redirect("/admin/dashboard/quiz")

@app.route("/edit/quiz", methods=["POST"])
@login_required
def edit_quiz():
    up_data = [
        request.form.get("name"),
        request.form.get("doq"),
        request.form.get("duration"),
        request.form.get("quiz_id")
    ]
    if(quiz.update(up_data)):
        flash(f"quiz updated sucessfully","info")
    else:
        flash("Error try again","info")
    return redirect(url_for("admin_quiz"))

@app.route("/delete/quiz", methods=["POST"])
@login_required
def del_quiz():
    quiz_id = request.form.get("quiz_id")
    if(quiz.remove(quiz_id)):
        flash(f"Quiz deleted sucessfully","info")
    else:
        flash("Error try again","info")
    return redirect(url_for("admin_quiz"))

@app.route("/get/addquiz",methods=["POST"])
def get_addquiz():
    sub_id = request.form.get("sub_id")
    return render_template("forms/addquiz.html",chaplist=chap.get(sub_id))

@app.route("/get/editquiz",methods=["POST"])
def get_editquiz():
    chap_id = request.form.get("chap_id")
    return render_template("forms/editquiz.html",quizlist=quiz.get(chap_id))

@app.route("/get/delquiz",methods=["POST"])
def get_delquiz():
    chap_id = request.form.get("chap_id")
    return render_template("forms/delquiz.html",quizlist=quiz.get(chap_id))

@app.route("/get/temp/editquiz",methods=["POST"])
def temp_editquiz():
    sub_id = request.form.get("sub_id")
    return render_template("forms/qechap.html",chaplist=chap.get(sub_id))

@app.route("/get/temp/delquiz",methods=["POST"])
def temp_delquiz():
    sub_id = request.form.get("sub_id")
    return render_template("forms/qdchap.html",chaplist=chap.get(sub_id))

############################################################ User Path
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