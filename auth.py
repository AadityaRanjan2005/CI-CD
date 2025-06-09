from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from models import User
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from Schemas import TokenData  
from database import get_db    
import logging                 


# Logging setup 
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# --- Auth and User Management ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """
    Function Task:
        Checks if the plain password entered by the user matches the hashed password stored in the database.

    Arguments:
        plain_password (str): The password entered by the user.
        hashed_password (str): The hashed password from the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    # logging.INFO(f'{plain_password}, {hashed_password}')
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, username: str):
    """
    Function Task:
        Looks up a user in the database using their username.

    Arguments:
        db (Session): The database session to use for the query.
        username (str): The username to search for.

    Returns:
        User or None: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """
    Function Task:
        Checks if the username and password are correct and returns the user if they are.

    Arguments:
        db (Session): The database session to use for the query.
        username (str): The username entered by the user.
        password (str): The plain password entered by the user.

    Returns:
        User or None: The user object if authentication is successful, otherwise None.
    """
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Function Task:
        Creates a JWT token that can be used to identify the user in future requests.

    Arguments:
        data (dict): Information to include in the token (like username).
        expires_delta (timedelta or None): How long the token should be valid for.

    Returns:
        str: The encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth_2_scheme), db: Session = Depends(get_db)):
    """
    Function Task:
        Decodes the JWT token from the request and returns the current user from the database.

    Arguments:
        token (str): The JWT token sent by the client.
        db (Session): The database session to use for the query.

    Returns:
        User: The user object for the currently authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("JWT decode failed: username missing")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        logger.warning("JWTError during token validation")
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        logger.warning(f"User not found: {token_data.username}")
        raise credentials_exception
    return user