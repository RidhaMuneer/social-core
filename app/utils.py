from passlib.context import CryptContext
import random
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Utils:
    def hash(password: str) -> str:
        return pwd_context.hash(password)


    def verify(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


    def generate_random_url(length: int) -> str:
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choices(characters, k=length))
        return random_string
