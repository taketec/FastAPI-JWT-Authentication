from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str)->str:
    """Takes a plain password and returns the hash for it so that
    it can be safely stored in the database."""
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    """Takes both the plain and the hashed passwords and 
    returns a boolean representing whether the two passwords
    match or not."""
    return password_context.verify(password, hashed_pass)