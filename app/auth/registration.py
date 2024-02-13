from passlib.context import CryptContext

pwd_content = CryptContext(schemes=['bcrypt'], deprecated='auto')