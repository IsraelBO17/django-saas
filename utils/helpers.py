import random
import string
from passlib.context import CryptContext

USER_VERIFY_ACCOUNT = 'verify-account'
USER_FORGOT_PASSWORD = 'password-reset'
SPECIAL_CHARACTERS = ['@','#','$','%','=',':','?','.','/','|','~','>']
# OTHER_SPECIAL_CHARACTERS ['&', '^', ';', '\\', '}', '<', '-', "'", '[', '+', ')', '*', '_', '`', '!', '(', ']', '"', ',', '{']


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_text(plain_text):
    return pwd_context.hash(plain_text)

def verify_hashed_text(plain_text, hashed_text):
    return pwd_context.verify(plain_text, hashed_text)

def generate_strong_password(length=12, include_special_chars=True):
    """
    Generates a strong password with the specified length.

    Args:
        length (int): The desired length of the password.
        include_special_chars (bool): Whether to include special characters.

    Returns:
        str: The generated password.
    """

    characters = string.ascii_letters + string.digits
    if include_special_chars:
        characters += string.punctuation

    password = ''.join(random.choice(characters) for _ in range(length))

    return password

def is_password_strong_enough(password: str) -> bool:
    if len(password) < 8:
        return False
    
    if not any(char.isupper() for char in password):
        return False
    
    if not any(char.islower() for char in password):
        return False
    
    if not any(char.isdigit() for char in password):
        return False
    
    if not any(char in SPECIAL_CHARACTERS for char in password):
        return False
    
    return True