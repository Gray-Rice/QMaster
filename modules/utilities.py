from flask import render_template
import modules.dbmanage as dbm

def check(key,data):
    for x in data:
        for i in x:
            i = str(i).lower()
            if(key in i or key == i):
                return x
    return False

def subswap(id):
    obj = dbm.subject()
    return obj.name(id)

def chapswap(id):
    obj = dbm.chapter()
    temp = [ obj.name(id) ]
    temp.append( subswap(obj.getsubject(id)) )
    return temp

def quizswap(id):
    obj = dbm.quiz()
    temp = [ obj.name(id) ]
    temp.extend(chapswap(obj.getchapter(id)))
    return temp

def process_quest(q):
    copt = q[-1]
    opt = q[3:-1]
    q = q[:3]
    q.extend([opt,copt])
    return q

def search(query,admin=False):
    match query[0].lower():
        case "user":
            if(admin != True):
                return "<p>Unauthorised action</p>"
            obj = dbm.users()
            result = check(query[1],obj.get())
            if(result):
                return render_template("search/user.html",result=result)
            else:
                query[0] = query[0].capitalize()
                return render_template("search/notfound.html",query=query)
        
        case "subject":
            obj = dbm.subject()
            result = check(query[1],obj.get())
            if(result):
                return render_template("search/subject.html",result=result)
            else:
                query[0] = query[0].capitalize()
                return render_template("search/notfound.html",query=query)
        
        case "chapter":
            obj = dbm.chapter()
            result = check(query[1],obj.get())
            if(result):
                result = list(result)
                # id,subject ,chap_code,name,description
                result[1] = subswap(result[1])
                return render_template("search/chapter.html",result=result)
            else:
                query[0] = query[0].capitalize()
                return render_template("search/notfound.html",query=query)
        
        case "quiz":
            obj = dbm.quiz()
            result = check(query[1],obj.get())
            if(result):
                result = list(result)
                # id,chapter_id,name,quiz_date,duration,description,chaper name,subject
                result.extend(chapswap(result[1]))
                return render_template("search/quiz.html",result=result)
            else:
                query[0] = query[0].capitalize()
                return render_template("search/notfound.html",query=query)
        
        case "question":
            obj = dbm.questions()
            result = check(query[1],obj.get())
            if(result):
                result = list(result)
                # id, quiz_id, qstatement, opt1, opt2, opt3, opt4, copt,quiz_name,chapter,subject
                result = process_quest(result)
                result.extend(quizswap(result[1]))
                return render_template("search/quest.html",result=result,admin=True)
            else:
                query[0] = query[0].capitalize()
                return render_template("search/notfound.html",query=query)