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

def add_user(user):
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

def search_user(username=None,id=None):
    with sqlite3.connect("data/instance.db") as conn:
        cursor = conn.cursor()
        if(username not in (None,"")):
            cursor.execute("SELECT id, username, password, role FROM Users WHERE username = ?",(username,))
        elif(id != None):
            cursor.execute("SELECT id, username, password, role FROM Users WHERE id = ?",(id,))
        user = cursor.fetchone()
        if user:
            print(f"User found: ID={user[0]}, Username={user[1]}")
            return {"id": user[0],"username": user[1],"password":user[2],"role": user[3] }
        else:
            print("User not found.")
            return None

def rm_user(username):
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

def get_role(username):
    with sqlite3.connect("data/instance.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM Users WHERE username = ?",(username,))
        user = cursor.fetchone()
        return user[0]
