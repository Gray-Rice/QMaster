import hashlib

def hashpwd(password):
    return hashlib.sha256(password.encode()).hexdigest()
    
def verify_hash(password, pwdhash):
    return hashpwd(password) == pwdhash

def verify_login(username,enteredpwd):
    from modules.dbmanage import search_user
    user = search_user(username)
    if  user != None:
        if verify_hash(enteredpwd,user["password"]):
            return True
    return False
