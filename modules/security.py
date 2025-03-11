import hashlib
import os
import pickle
import sqlite3
from datetime import date
import secrets

def create_token(user_id):
    with sqlite3.connect("data/instance.db") as con:
        try:
            token = secrets.token_hex(32)
            cur = con.cursor()
            cur.execute("INSERT INTO Api (user_id,token) VALUES (?,?)",(user_id,token))
            con.commit()
            print("Created API")
            return True
        except Exception as e:
            print("API creation error : "+str(e))
            return False

def get_token(user_id):
    with sqlite3.connect("data/instance.db") as con:
        cur = con.cursor()
        cur.execute("SELECT token FROM Api WHERE user_id = ?",(user_id,))
        token = cur.fetchone()
        if(token):
            return token[0]
        else:
            print("User has no active API tokens")
            return None

def check_token(token):
    with sqlite3.connect("data/instance.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Api WHERE token = ? ",(token,))
        api = cur.fetchone()
        if(api):
            print(f"API Authorized for user ID: {api[1]}")
            return True
        else:
            return False

def start_checkup():
    if(not setup_check()):
        print("Creating new instance....")
        create_instance()
    else:
        print("Instance exists proceeding")

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
        with sqlite3.connect("data/instance.db") as con:
            with open("data/dbschema.sql", "r") as f:
                con.executescript(f.read())
                print("Database initialized successfully!")
                setup["dbstat"] = True
                cur = con.cursor()
                # Implement setting alternate password through command line or env
                cur.execute(f'''INSERT INTO Users VALUES (0,'admin@qm.com', '{hashpwd("admin")}', 'admin','admin','2005-1-1','admin')''')
                con.commit()
                print("Admin added with defaults.")
                if(create_token(0)):
                    print("API Token for admin added Login to view")
            with open("data/admin_lock.pkl","wb") as lock:
                pickle.dump(setup,lock)
    except FileNotFoundError:
        print("Schema not found verify if all files are present and correct")

def hashpwd(password): 
    return hashlib.sha256(password.encode()).hexdigest()
    
def verify_hash(password, pwdhash):
    return hashpwd(password) == pwdhash

def verify_login(username,enteredpwd):
    from modules.dbmanage import users
    obj = users()
    user = obj.search(username)
    if  user != None:
        if verify_hash(enteredpwd,user["pwd"]):
            del user["pwd"]
            return (True,user)
        return (False,"pwd")
    return (False,"usr")

