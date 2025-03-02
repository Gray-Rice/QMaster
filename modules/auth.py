import hashlib

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
