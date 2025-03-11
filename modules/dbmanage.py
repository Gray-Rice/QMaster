import sqlite3
from datetime import date
from modules.security import hashpwd

    
def get_role(username):
    with sqlite3.connect("data/instance.db") as con:
        cur = con.cursor()
        cur.execute("SELECT role FROM Users WHERE username = ?",(username,))
        user = cur.fetchone()
        if(user != None):
            return user[0]

class users():
    def add(self,user):
        with sqlite3.connect("data/instance.db") as con:
            try:
                user[0] = user[0].strip()
                user[1] = hashpwd(user[1].strip())
                cur = con.cursor()
                cur.execute(f'''INSERT INTO Users (username, password, fullname, qualification, dob) VALUES (?,?,?,?,?)''',user)
                con.commit()
                print("Added User: "+user[0])
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

    def get(self,username=None):
        with sqlite3.connect("data/instance.db") as con:
                cur = con.cursor()
                if(username == None):
                    cur.execute(f'''SELECT id,username,fullname,qualification,dob from Users''')
                    users = cur.fetchall()
                    users.pop(0)
                else:
                    cur.execute(f"SELECT id,username,fullname,qualification,dob from Users WHERE username = ?",(username,))
                    users = cur.fetchone()
                return users
    def username(self,user_id):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT username from Users WHERE id = ?''',(user_id,))
            user = cur.fetchone()
            return user[0]

    def search(self,username=None,id=None):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            if(username not in (None,"")):
                cur.execute("SELECT id, username, password, fullname, qualification, dob, role FROM Users WHERE username = ?",(username,))
            elif(id != None):
                cur.execute("SELECT id, username, password, fullname, qualification, dob, role FROM Users WHERE id = ?",(id,))
            user = cur.fetchone()
            if user:
                print(f"User found: ID={user[0]}, Username={user[1]}")
                return {"id": user[0],"username": user[1],"pwd":user[2],"fname":user[3],"qual":user[4],"dob":user[5],"role": user[6] }
            else:
                print("User not found.")
                return None

    def remove(self,user_id):
        if user_id == 0:
                print("Cannot delete the admin user!")
                return
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute("DELETE FROM Users WHERE id = ?", (user_id,))
                con.commit()
                print(f"User deleted successfully.")
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

class subject:
    def add(self,sub_data):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute(f'''INSERT INTO Subjects (code,name, description) VALUES (?,?,?)''',sub_data)
                con.commit()
                print("Added Subject: "+sub_data[1])
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

    def get(self):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT * from Subjects''')
            subjects = cur.fetchall()
            return subjects

    def name(self,id):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT name from Subjects WHERE id = ?''',(id,))
            subject = cur.fetchone()
            return subject[0]

    def remove(self,sub_id):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")
                cur.execute("DELETE FROM Subjects WHERE id = ?", (sub_id,))
                con.commit()
                print(f"Subject '{sub_id}' deleted successfully.")
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False
    
    def update(self,up_data):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            try:
                con.execute("UPDATE Subjects SET name = ?, description = ? WHERE id = ?",up_data)
                con.commit()
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

# Chapter
class chapter:
    def add(self,chap_data):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute('''INSERT INTO Chapters (subject_id, chap_code, name, description) VALUES (?,?,?,?)''',chap_data)
                con.commit()
                return True
                print("Added Chapter: "+chap_data[2])
            except Exception as e:
                print("Exception : "+str(e))
                return False

    def get(self,sub_id=None):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            if(sub_id != None):
                cur.execute(f'''SELECT id,chap_code,name,description from Chapters WHERE subject_id = ?''',(sub_id,))
            else:
                cur.execute("SELECT * from Chapters")
            chapters = cur.fetchall()
            return chapters

    def name(self,id):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT name from Chapters WHERE id = ?''',(id,))
            chapter = cur.fetchone()
            return chapter[0]

    def getsubject(self,id):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT subject_id from Chapters WHERE id = ?''',(id,))
            subject = cur.fetchone()
            return subject[0]

    def remove(self,chap_id):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute("PRAGMA foreign_keys = ON;") # To enable cascading on delete
                cur.execute("DELETE FROM Chapters WHERE id = ?", (chap_id,))
                con.commit()
                print(f"Chapter '{chap_id}' deleted successfully.")
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False
    
    def update(self,up_data):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            try:
                con.execute("UPDATE Chapters SET name = ?, description = ? WHERE id = ?",up_data)
                con.commit()
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

# Quiz
class quiz:
    def add(self,quiz_data):
        with sqlite3.connect("data/instance.db") as con:
            try :
                cur = con.cursor()
                cur.execute('''INSERT INTO Quiz (chapter_id,name,start_date,end_date,duration,description) VALUES (?,?,?,?,?,?)''',quiz_data)
                con.commit()
                print("Quiz Added")
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

    def get(self,chapter_id=None,quiz_id=None):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            if(chapter_id != None):
                cur.execute(f'''SELECT * FROM Quiz WHERE chapter_id = ?''',(chapter_id,))
            elif(quiz_id != None):
                cur.execute(f'''SELECT * FROM Quiz WHERE id = ?''',(quiz_id,))
            else:
                cur.execute("SELECT * FROM Quiz")
            quizes = cur.fetchall()
            return quizes
    
    def name(self,id):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT name from Quiz WHERE id = ?''',(id,))
            quiz = cur.fetchone()
            return quiz[0]
    
    def getchapter(self,id):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT chapter_id from Quiz WHERE id = ?''',(id,))
            chapter = cur.fetchone()
            return chapter[0]
    
    def update(self,up_data):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            try:
                con.execute("UPDATE Quiz SET name = ?, quiz_date = ?,duration = ? WHERE id = ?",up_data)
                con.commit()
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

    def remove(self,quiz_id):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")
                cur.execute("DELETE FROM Quiz WHERE id = ?", (quiz_id,))
                con.commit()
                print(f"Quiz '{quiz_id}' deleted successfully.")
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

#  Questions
class questions:
    def add(self,questions):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                for q in questions:
                    cur.execute('''INSERT INTO Questions (quiz_id, qstatement, opt1,opt2,opt3,opt4,copt) VALUES (?,?,?,?,?,?,?)''',q)
                con.commit()
                print("Questions added")
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

    def get(self,quiz_id=None):
        with sqlite3.connect("data/instance.db") as con:
            # try:
            cur = con.cursor()
            if(quiz_id != None):
                cur.execute(f'''SELECT * FROM Questions WHERE quiz_id = ?''',(quiz_id,))
            else:
                cur.execute("SELECT * FROM Questions")
            questions = cur.fetchall()
            return questions

    def update(self,up_data):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            try:
                con.execute("UPDATE Questions SET qstatement = ?,opt1 = ?,opt2 = ?,opt3  = ?,opt4  = ?,copt = ? WHERE id = ?",up_data)
                con.commit()
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

    def remove(self,qid):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute("PRAGMA foreign_keys = ON;") 
                cur.execute("DELETE FROM Questions WHERE id = ?", (qid,))
                con.commit()
                print(f"Question '{qid}' deleted successfully.")
            except Exception as e:
                print("Exception : "+str(e))
                return False

# Scores
class score:
    def add(self,score_data):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute(f'''INSERT INTO Scores (quiz_id, user_id, report,marks,ratio) VALUES (?,?,?,?,?)''',score_data)
                con.commit()
                print("Attempt Recorded")
                return True
            except sqlite3.IntegrityError :
                return False

    def get_report(self,report_id):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT quiz_id,marks,ratio,report,time_stamp FROM Scores WHERE id = ?''',(report_id,))
            report = cur.fetchall()
            return report[0]

    def get(self,user_id=None,quiz_id=None):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            if( user_id == None and quiz_id != None):
                cur.execute(f'''SELECT * FROM Scores WHERE quiz_id = ?''',(quiz_id,))
            elif( user_id != None and quiz_id == None):
                cur.execute(f'''SELECT quiz_id,id,time_stamp,marks,ratio FROM Scores WHERE user_id = ?''',(user_id,))
            elif(user_id and quiz_id):
                cur.execute(f'''SELECT * FROM Scores WHERE quiz_id = ? AND user_id = ?''',(quiz_id,user_id))
            else:
                cur.execute("SELECT * FROM Scores")
            scores = cur.fetchall()
            return scores