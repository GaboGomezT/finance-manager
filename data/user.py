from infrastructure.mongo import db
from passlib.handlers.sha2_crypt import sha512_crypt as crypto

def register_user(name: str, email:str, password: str):
    # first check if the user already exists
    existing_user = db.users.count_documents({"email": email})
    if existing_user != 0:
        return "Este correo ya existe"
    
    db.users.insert_one({
        "name": name,
        "email": email,
        "password_hash": crypto.hash(password, rounds=172_434)
    })
    return None


def login_user(email:str, password: str):
    # first check if the user already exists
    existing_user = db.users.find_one({"email": email})
    if not existing_user:
        return "Este correo no existe"
    
    if not crypto.verify(password, existing_user["password_hash"]):
        return "Wrong password"
    return None

