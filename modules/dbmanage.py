import pickle
import os
import sqlite3
from datetime import date
from modules.auth import hashpwd
 

def setup_check():
    if(not os.path.exists("data/instance.db")):
        return False
    try:
        with open("data/admin_lock.pkl","rb") as f:
            setup = pickle.load(f)
            if(setup["dbstat"] == True):
                return True
            return False
            
    except FileNotFoundError:
        print("New Instance, Setup needed")
        return False

def create_instance():
    setup = {"dbstat":False,"admin@qm.com":"admin","instDate":date.today() }
    try:
        with sqlite3.connect("data/instance.db") as conn:
            with open("data/dbschema.sql", "r") as f:
                conn.executescript(f.read())
                print("Database initialized successfully!")
                setup["dbstat"] = True
                cursor = conn.cursor()
                # Implement setting alternate password through command line or env
                cursor.execute(f'''INSERT INTO Users VALUES (0,'admin@qm.com', '{hashpwd("admin")}', 'admin','admin','2005-1-1','admin')''')
                conn.commit()
                print("Admin added with defaults.")
            with open("data/admin_lock.pkl","wb") as lock:
                pickle.dump(setup,lock)
    
    except FileNotFoundError:
        print("Schema not found verify if all files are present and correct")
    
def start_checkup():
    if(not setup_check()):
        #c = input("No instance found or instance broken: Create New instance ? (y/n): ")
        #if(c.lower() == "y"):
        print("Creating new instance....")
        create_instance()
    else:
        print("Instance exists proceeding")

def get_role(username):
    with sqlite3.connect("data/instance.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM Users WHERE username = ?",(username,))
        user = cursor.fetchone()
        return user[0]

class users():
    def add(self,user):
        # Format = list username,password,fname,qual,dob
        with sqlite3.connect("data/instance.db") as conn:
            try:
                user[0] = user[0].strip()
                user[1] = hashpwd(user[1].strip())
                cursor = conn.cursor()
                cursor.execute(f'''INSERT INTO Users (username, password, fullname, qualification, dob) VALUES (?,?,?,?,?)''',user)
                conn.commit()
                return True
            except sqlite3.IntegrityError :
                return False

    def get(self):
        with sqlite3.connect("data/instance.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f'''SELECT id,username,fullname,qualification,dob from Users''')
                users = cursor.fetchall()
                users.pop(0)
                return users

    def search(self,username=None,id=None):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            if(username not in (None,"")):
                cursor.execute("SELECT id, username, password, fullname, qualification, dob, role FROM Users WHERE username = ?",(username,))
            elif(id != None):
                cursor.execute("SELECT id, username, password, fullname, qualification, dob, role FROM Users WHERE id = ?",(id,))
            user = cursor.fetchone()
            if user:
                print(f"User found: ID={user[0]}, Username={user[1]}")
                return {"id": user[0],"username": user[1],"pwd":user[2],"fname":user[3],"qual":user[4],"dob":user[5],"role": user[6] }
            else:
                print("User not found.")
                return None

    def remove(self,username):
        if username == "admin":
                print("Cannot delete the admin user!")
                return
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM Users WHERE username = ?",(username,))
            user = cursor.fetchone()
            if not user:
                print(f"User not found.")
                return
            # Delete
            cursor.execute("DELETE FROM Users WHERE username = ?", (username,))
            conn.commit()
            print(f"User '{username}' deleted successfully.")

class subject:
    def add(self,sub_data):
        with sqlite3.connect("data/instance.db") as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f'''INSERT INTO Subject (code,name, description) VALUES (?,?,?)''',sub_data)
                conn.commit()
                return True
            except sqlite3.IntegrityError :
                return False

    def get(self,user_id = None):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            if(user_id == None):
                cursor.execute(f'''SELECT * from Subject''')
            else:
                cursor.exeute(f'''SELECT  s.id,s.name,s.description
                                    FROM Subject s,Enrolled e
                                    WHERE e.subject_id = s.id AND e.user_id = ?;''',(user_id,))
            subjects = cursor.fetchall()
            return subjects

    def remove(self,sub_id):
        with sqlite3.connect("data/instance.db") as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;") # To enable cascading on delete
                # Delete
                cursor.execute("DELETE FROM Subject WHERE id = ?", (sub_id,))
                conn.commit()
                print(f"Subject '{sub_id}' deleted successfully.")
                return True
            except Exception:
                return False
    
    def update(self,up_data):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            try:
                conn.execute("UPDATE Subject SET name = ?, description = ? WHERE id = ?",up_data)
                conn.commit()
                return True
            except Exception:
                return False


# Chapter
class chapter:
    def add(self,chap_data):
        with sqlite3.connect("data/instance.db") as conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO Chapter (subject_id, chap_code, name, description) VALUES (?,?,?,?)''',chap_data)
                conn.commit()
                return True
            except sqlite3.IntegrityError :
                return False

    def get(self,sub_id):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f'''SELECT id,chap_code , name, description from Chapter WHERE subject_id = ?''',(sub_id,))
            chapters = cursor.fetchall()
            return chapters

    def remove(self,chap_id):
        with sqlite3.connect("data/instance.db") as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;") # To enable cascading on delete
                cursor.execute("DELETE FROM Chapter WHERE id = ?", (chap_id,))
                conn.commit()
                print(f"Chapter '{chap_id}' deleted successfully.")
                return True
            except Exception:
                return False
    
    def update(self,up_data):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            try:
                conn.execute("UPDATE Chapter SET name = ?, description = ? WHERE id = ?",up_data)
                conn.commit()
                return True
            except Exception:
                return False

# Quiz
class quiz:
    def add(self,quiz_data):
        with sqlite3.connect("data/instance.db") as conn:
            try :
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO Quiz (chapter_id,name,quiz_date,duration,description) VALUES (?,?,?,?,?)''',quiz_data)
                conn.commit()
                print("Quiz Added")
                return True
            except Exception:
                return False

    def get(self,chapter_id):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f'''SELECT * FROM Quiz WHERE chapter_id = ?''',(chapter_id,))
            quizes = cursor.fetchall()
            return quizes

    def remove(self,quiz_id):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;") # To enable cascading on delete
            # Delete
            cursor.execute("DELETE FROM Quiz WHERE id = ?", (quiz_id,))
            conn.commit()
            print(f"Quiz '{quiz_id}' deleted successfully.")

#  Questions
class questions:
    def add(self,questions):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            for q in questions:
                cursor.execute('''INSERT INTO Question (quiz_id, qstatement, opt1,opt2,opt3,opt4,copt) VALUES (?,?,?,?,?,?,?)''',q)
            conn.commit()
            print("Questions added")

    def get(self,quiz_id):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f'''SELECT * FROM Question WHERE quiz_id = ?''',(quiz_id,))
            questions = cursor.fetchall()
            return questions
    def remove(self,qid):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;") # To enable cascading on delete
            # Delete
            cursor.execute("DELETE FROM Question WHERE id = ?", (qid,))
            conn.commit()
            print(f"Question '{qid}' deleted successfully.")

# Scores
class score:
    def add(self,score_data):
        with sqlite3.connect("data/instance.db") as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f'''INSERT INTO Score (quiz_id, user_id, time_stamp, total_score) VALUES (?,?,?,?)''',score_data)
                conn.commit()
                return True
            except sqlite3.IntegrityError :
                return False

    def get(self,user_id=None,quiz_id=None):
        with sqlite3.connect("data/instance.db") as conn:
            cursor = conn.cursor()
            if( user_id == None and quiz_id != None):
                cursor.execute(f'''SELECT * FROM Score WHERE quiz_id = ?''',(quiz_id,))
            elif( user_id != None and quiz_id == None):
                cursor.execute(f'''SELECT * FROM Score WHERE user_id = ?''',(user_id,))
            scores = cursor.fetchall()
            return scores