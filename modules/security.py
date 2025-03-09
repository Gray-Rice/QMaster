import hashlib
import os
import pickle
import sqlite3
from datetime import date

def start_checkup():
    if(not setup_check()):
        #c = input("No instance found or instance broken: Create New instance ? (y/n): ")
        #if(c.lower() == "y"):
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

