import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    prehash = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(prehash)


def verify_password(password: str, hash: str) -> bool:
    prehash = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.verify(prehash, hash)




