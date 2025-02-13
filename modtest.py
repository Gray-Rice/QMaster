import modules.dbmanage as dbm
from modules.auth  import *

def login(username,enteredpwd):
    user = dbm.search_user(username)
    if  user != None:
        if verify_hash(enteredpwd,user["password"]):
            return True
    return False

dbm.start_checkup()

dbm.rm_user("dum")
dbm.add_user("dum","123")

if (login("dum","123")):
    print("kjbfds")