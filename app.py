from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_restful import Resource, Api
from ast import literal_eval

# User-defined modules
import modules.dbmanage as dbm
import modules.security as sec
import modules.utilities as util
from modules.utilities import apitools

uobj = dbm.users()
sub = dbm.subject()
chap = dbm.chapter()
quiz = dbm.quiz()
quest = dbm.questions()
sco = dbm.score()

app = Flask(__name__)
print("Getting Secrets....")
secrets = sec.get_secrets()
if(secrets != None):
    app.secret_key = secrets["SECRET_KEY"]
else:
    print("Secrets Missing Exiting.....")
    exit()

api = Api(app)

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
    if(role == None):
        flash("User Not Found","info")
        redirect(url_for("login"))
    return User(username,role)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        valid = sec.verify_login(username, password)
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
    if request.method == "POST":
        # POST response
        user_data = [
            request.form.get('username').strip(),
            request.form.get('password').strip(),
            request.form.get('fullname').strip(),
            request.form.get('qualification').strip(),
            request.form.get('dob'),
        ]
        if(not util.valid_mail(user_data[0])):
            return render_template("register.html",message="Username Error: Not a valid mail")
        for i in user_data:
            if(i == ""):
                return render_template("register.html",message="Input Error: Check if values entered are correct")
        if(uobj.add(user_data)):
            flash("Registration sucessfully<br>Login to Proceed","info")
            return redirect("/login")
        else:
            return render_template("register.html",message=(f"Username {user_data[0]} already exists."))
    return render_template("register.html")

################################################################### API

class subject_api(Resource):
    def get(self):
        token = request.headers.get("X-API-KEY")
        if (not sec.check_token(token)):
            return {"Error": "Unauthorized - Invalid or No API Key Provided"}, 401
        subjects = apitools.get_sub()
        if (subjects):
            return jsonify({"Subjects": subjects})
        return {"Error": "No subjects found"}, 204
        

class chapter_api(Resource):
    def get(self):
        token = request.headers.get("X-API-KEY")
        if (not sec.check_token(token)):
            return {"Error": "Unauthorized - Invalid or No API Key Provided"}, 401
        chapters = apitools.get_chap()
        if (chapters):
            return jsonify({"Chapters": chapters})
        return {"Error": "No chapters found"}, 204
        

class quiz_api(Resource):
    def get(self):
        token = request.headers.get("X-API-KEY")
        if (not sec.check_token(token)):
            return {"Error": "Unauthorized - Invalid or No API Key Provided"}, 401
        quizzes = apitools.get_quiz()
        if (quizzes):
            return jsonify({"Quizzes":quizzes})
        return {"Error": "No Quiz found"}, 204
        

class score_api(Resource):
    def get(self):
        token = request.headers.get("X-API-KEY")
        if (not sec.check_token(token)):
            return {"Error": "Unauthorized - Invalid or No API Key Provided"} ,401
        scores = apitools.get_score()
        if (scores):
            return jsonify({"scores": scores})
        return {"Error": "No scoress found"} ,204
        

api.add_resource(subject_api, "/api/subjects")
api.add_resource(chapter_api, "/api/chapters")
api.add_resource(quiz_api, "/api/quiz")
api.add_resource(score_api, "/api/scores")


################################################################### Protected Routes

######################################################### Scores
@app.route('/user/report/<int:report_id>/')
@login_required 
def view_report(report_id):
    at = sco.get_report(report_id)
    score = at[1]
    ratio = literal_eval(at[2])
    report = literal_eval(at[3])
    time = at[4]
    return render_template("score/report.html",user=session["user"]["fname"],quiz=quiz.name(at[0]),score=score,ratio=ratio,report=report,time=time)

@app.route('/user/scores/')
@login_required
def view_score():
    user_id = session["user"]["id"]
    alist = {}
    for i in sco.get(user_id):
        temp = [ i[1],
            i[2],
            i[3],
            literal_eval(i[4])
        ]
        key = quiz.name(i[0])
        if(key not in alist):
            alist[key] = [temp,]
        else:
            alist[key].append(temp)
    if(alist == []):
        alist=None
    return render_template("score/attempts.html",alist=alist,user=session["user"]["fname"])

@app.route('/score/save/<int:quiz_id>/',methods=['POST'])
@login_required 
def store_quiz(quiz_id):
    user_id = session["user"]["id"]
    qlist,akey = session["quiz_con"]
    uans = {}
    report = {}
    score = 0
    unat = 0
    j=0
    for i in akey.keys():
        temp = [ request.form.get(i),akey[i] ]
        uans[i]  = temp[0]
        temp.append(uans[i] == akey[i])
        if(temp[-1]):
            score += 1
        report[j+1] = [qlist[j][2]]+ temp
        j+=1
        if (uans[i] == None):
            unat += 1
    ratio = [len(akey),unat]
    score_data = [quiz_id ,user_id, str(report),score,str(ratio)]
    if(sco.add(score_data)):
        return render_template("score/submit.html",user=session["user"]["fname"],quiz_id=quiz_id,score=score,ratio=ratio,report=report)
    else:
        return "Error ocured try again"

############################################################ User Path
@app.route('/user/')
@login_required  
def user_dashboard():
    user = session["user"]
    q = util.timegate([ list(x) for x in  quiz.get()])
    q = util.parse_name(q)
    print(q)
    return render_template("user/dashboard.html",user=user["fname"],sublist=sub.get(),quizlist=q)

@app.route('/user/quiz/<int:quiz_id>')
@login_required 
def user_quiz(quiz_id):
    dur = int(quiz.get(quiz_id=quiz_id)[0][5]) * 60 
    qlist,ans = util.strip_ans(quest.get(quiz_id))
    session["quiz_con"] = [qlist,ans]
    return render_template("user/quiz.html",user=session["user"],qlist=qlist,quiz_id=quiz_id,dur=dur)

############################################################ Search

@app.route('/search',methods=["GET","POST"])
@login_required  
def search():
    if(request.method == "GET"):
        user = session["user"]
        return render_template("search/search.html",role=user["role"],user=user["fname"])
    query = [request.form.get("category"),request.form.get("keyword")]
    if(current_user.role != "admin"):
        return util.search(query)
    else:
        return util.search(query,True)

############################################################ API
@app.route('/add/api',methods=["POST"])
@login_required  
def add_api():
    if(current_user.role != "admin"):
        return "Error unauthorised <a href=/user>Go Back</a>"
    user_id = request.form.get("user_id")
    if(sec.create_token(user_id)):
        flash("API Token Created","info")
    else:
        flash("Error Creating Token","info")
    return redirect(url_for("admin_api"))

@app.route('/delete/api',methods=["POST"])
@login_required  
def del_api():
    if(current_user.role != "admin"):
        return "Error unauthorised <a href=/user>Go Back</a>"
    user_id = request.form.get("user_id")
    if(sec.rm_token(user_id)):
        flash("API Token Deleted","info")
    else:
        flash("Error Deleting Token","info")
    return redirect(url_for("admin_api"))

############################################################ Admin Paths
@app.route('/admin/')
@login_required  
def admin_dashboard():
    if(current_user.role != "admin"):
        return "Error unauthorised <a href=/user>Go Back</a>"
    return render_template("admin/dashboard.html",user="Admin")

@app.route('/admin/api')
@login_required  
def admin_api():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin/api.html",user="Admin",userlist=uobj.get(),admin_token=sec.get_token(0),tokenlist=sec.active_tokens())

@app.route('/admin/user')
@login_required  
def admin_user():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin/users.html",user="Admin",userlist=uobj.get())

@app.route('/admin/subject')
@login_required  
def admin_subject():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin/subject.html",user="Admin",sublist=sub.get())

@app.route('/admin/quiz')
@login_required  
def admin_quiz():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin/quiz.html",user="Admin",sublist=sub.get())


@app.route('/admin/questions')
@login_required  
def admin_question():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin/questions.html",user="Admin",quizlist=quiz.get())

@app.route('/admin/chapter')
@login_required  
def admin_chapter():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    return render_template("admin/chapter.html",user="Admin",sublist=sub.get())


############################################################ User Management
@app.route('/add/user/',methods=["POST"])
@login_required  
def add_user():
    user_data = [
            request.form.get('username').strip(),
            request.form.get('password').strip(),
            request.form.get('fullname').strip(),
            request.form.get('qualification').strip(),
            request.form.get('dob'),
        ]
    if(not util.valid_mail(user_data[0])):
        flash("Username Error: Not a valid mail","info")
        return redirect(url_for("admin_user"))
    for i in user_data:
        if(i == ""):
            flash("Input Error: Check if values entered are correct","info")
            return redirect(url_for("admin_user"))
    if(uobj.add(user_data)):
        flash("User added succesfully","info")
        return redirect(url_for("admin_user"))
    else:
        flash(f"Username {user_data[0]} already exist.","info")
        return redirect(url_for("admin_user"))

@app.route('/delete/user/',methods=["POST"])
@login_required 
def del_user():
    if(current_user.role != "admin"):
            return "Error unauthorised <a href=/user>Go Back</a>"
    user_id = request.form.get("user_id")
    if(uobj.remove(user_id)):
        flash("User removed","info")
    else:
        flash("Error Occured","info")
    return redirect(url_for("admin_user"))

############################################################ Questions

@app.route('/add/questions/',methods=["GET","POST"])
@login_required  
def add_question():
    if(current_user.role != "admin"):
        return "Error unauthorised"
    quest_d = session["quest_d"]
    if request.method == "POST":
        quiz_id = quest_d[0]
        n = quest_d[1]
        quest_data = []
        for i in range (0,n):
            # (quiz_id, qstatement, opt1,opt2,opt3,opt4,copt)
            temp = [ quiz_id,request.form.get(f'qstatement_{i}').strip().capitalize()]
            for j in range(0,4):
                temp.append( request.form.get(f'opt{i}_{j}').strip().capitalize() )
            temp.append( int(request.form.get(f'copt_{i}')) )
            quest_data.append(temp)
        if(quest.add(quest_data)):
            mesg = "Successfully added questions"
        else:
            mesg = "Error Try again"
        flash(mesg,"info")
        return redirect(url_for("admin_question"))
    return render_template("forms/quest/add.html",n=quest_d[1])

@app.route('/edit/question',methods=["POST"])
@login_required
def edit_quest():
    up_data = [ request.form.get('qstatement').strip(),]
    for j in range(0,4):
        up_data.append( request.form.get(f'opt{j}').strip() )
    up_data.extend( [int(request.form.get(f'copt')), session["quest_d"] ] )
    if(quest.update(up_data)):
        flash(f"Question updated sucessfully","info")
    else:
        flash("Error try again","info")
    return redirect(url_for("admin_question"))

@app.route("/delete/question", methods=["POST"])
@login_required
def del_quest():
    quest_id = request.form.get("quest_id")
    if(quest.remove(quest_id)):
        flash(f"Question deleted sucessfully","info")
    else:
        flash("Error try again","info")
    return redirect(url_for("admin_question"))

@app.route("/get/quest",methods=["POST"])
def get_quest():
    reqtype = request.form.get("reqtype")
    if(reqtype == "add"):
        session["quest_d"] = [
        request.form.get("quiz_id"),
        int(request.form.get("n")),
        ]
        return redirect(url_for("add_question"))

    elif(reqtype == "edit-temp"):
        return render_template("forms/quest/temp_edit.html",questlist=quest.get(request.form.get("quiz_id")))
    elif(reqtype == "del"):
        return render_template("forms/quest/delete.html",questlist=quest.get(request.form.get("quiz_id")))
    elif(reqtype == "edit"):
        session["quest_d"] = request.form.get("quest_id")
        return render_template("forms/quest/edit.html")

############################################################ Subject paths
@app.route("/add/subject",methods=["POST"])
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

@app.route("/add/chapter",methods=["POST"])
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
    return redirect(url_for("admin_chapter"))

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

@app.route("/get/chapter",methods=["POST"])
def get_chapter():
    reqtype = request.form.get("reqtype")
    if(reqtype == "edit"):
        sub_id = request.form.get("sub_id")
        return render_template("forms/chapter/edit.html",chaplist=chap.get(sub_id))
    elif(reqtype == "del"):
        sub_id = request.form.get("sub_id")
        return render_template("forms/chapter/delete.html",chaplist=chap.get(sub_id))


############################################################ Quiz path
@app.route("/add/quiz",methods=["POST"])
@login_required
def add_quiz():
    if(current_user.role != "admin"):
        return "<p>Error unauthorised</p>"
    quiz_data = [
        request.form.get("chap_id").strip(),
        request.form.get("name").strip(),
        request.form.get('start').replace("T", " "),
        request.form.get('end').replace("T", " "),
        request.form.get('duration'),
        request.form.get('description').strip(),
    ]
    if(quiz.add(quiz_data)):
        message =  f"\"{quiz_data[1]}\" added successfully"
    else:
        message =  f"\"{quiz_data[1]}\" already exists"
    flash(message,"info")
    return redirect(url_for("admin_quiz"))

@app.route("/edit/quiz", methods=["POST"])
@login_required
def edit_quiz():
    up_data = [
        request.form.get("name"),
        request.form.get("start").replace("T", " "),
        request.form.get('end').replace("T", " "),
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

@app.route("/get/quiz",methods=["POST"])
def get_quiz():
    reqtype = request.form.get("reqtype")
    if(reqtype == "add"):
        sub_id = request.form.get("sub_id")
        return render_template("forms/quiz/add.html",chaplist=chap.get(sub_id))
    elif(reqtype == "edit-temp"):
        sub_id = request.form.get("sub_id")
        return render_template("forms/quiz/temp_edit.html",chaplist=chap.get(sub_id))
    elif(reqtype == "edit"):
        chap_id = request.form.get("chap_id")
        return render_template("forms/quiz/edit.html",quizlist=quiz.get(chap_id))
    elif(reqtype == "del-temp"):
        sub_id = request.form.get("sub_id")
        return render_template("forms/quiz/temp_del.html",chaplist=chap.get(sub_id))
    elif(reqtype == "del"):
        chap_id = request.form.get("chap_id")
        return render_template("forms/quiz/delete.html",quizlist=quiz.get(chap_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logout successful.","info")
    return redirect("/login")

if __name__ == '__main__':
    sec.start_checkup()
    app.run(host="0.0.0.0",debug=True)