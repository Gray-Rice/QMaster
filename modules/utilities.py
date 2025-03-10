from flask import render_template,jsonify
import modules.dbmanage as dbm
from datetime import datetime
from ast import literal_eval

class apitools():
    @staticmethod
    def get_sub():
        obj = dbm.subject()
        out = []
        for i in obj.get():
            temp = {}
            temp["id"] = i[0]
            temp["code"] = i[1]
            temp["name"] = i[2]
            temp["decription"] = i[3]
            out.append(temp)
        return out
    
    @staticmethod
    def get_chap():
        obj = dbm.chapter()
        sub = dbm.subject()
        out = []
        for i in obj.get():
            temp = {}
            temp["id"] = i[0]
            temp["subject"] = subswap(i[0])
            temp["code"] = i[2]
            temp["name"] = i[3]
            temp["decription"] = i[4]
            out.append(temp)
        return out
    
    @staticmethod
    def get_quiz():
        obj = dbm.quiz()
        out = []
        for i in obj.get():
            temp = {}
            temp["id"] = i[0]
            temp["chapter"],temp["subject"] = chapswap(i[1])
            temp["name"] = i[2]
            temp["start_date"] = i[3]
            temp["end_date"] = i[4]
            temp["duration"] = i[5]
            temp["decription"] = i[6]
            out.append(temp)
        return out

    @staticmethod
    def get_score():
        obj = dbm.score()
        out = {}
        for i in obj.get():
            temp = {}
            temp["id"] = i[0]
            temp["name"],temp["chapter"],temp["subject"] = quizswap(i[1])
            temp["time"] = i[3]
            temp["score"] = i[5]
            temp["total"],temp["unattempted"] = literal_eval(i[6])
            temp["incorrect"] = temp["total"] - temp["score"]
            temp["report"] = literal_eval(i[4])
            user = userswap(i[2])
            if(user in out.keys()):
                out[user].append(temp)
            else:
                out[user] = [temp,]
        return out


def parse_name(q):
    chap = dbm.chapter()
    sub = dbm.subject()
    for i in q:
        id = chap.getsubject(i[1])
        i.append(sub.name(id))
        i[1] = chap.name(i[1])
    return q

def timegate(qlist):
    # [1, 1, 'Quiz1', '2025-03-01 09:00', '2025-03-14 12:59', '1', 'Introduction to quiz system']
    cur = datetime.now()
    for i in qlist:
        start = datetime.strptime(i[3], "%Y-%m-%d %H:%M")
        end = datetime.strptime(i[4], "%Y-%m-%d %H:%M")
        i.append( cur >= start and cur <= end )
    return qlist

def check(key,data):
    for x in data:
        for i in x:
            i = str(i).lower()
            if(key in i or key == i):
                return x
    return False

def userswap(id):
    obj = dbm.users()
    return obj.username(id)

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

def process_quest(q,rm=False):
    copt = q[-1]
    opt = [ x for x in q[3:-1] if(x != "" or not rm)]
    q = q[:3]
    q.extend([opt,copt])
    return q

def strip_ans(qlist):
    qs = []
    ans = {}
    for i in qlist:
        quest = process_quest(list(i),True)[:-1]
        qs.append( quest )
        ans[i[0]] = quest[-1][i[-1]-1]
    return qs,ans


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