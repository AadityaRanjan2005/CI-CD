from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """SQLAlchemy model for User.
    This class defines the structure of the 'users' table in the database.
        Attributes:
        username (str): The unique username of the user.
        full_name (str): The full name of the user.
        email (str): The email address of the user, must be unique.
        hashed_password (str): The hashed password of the user.
        disabled (bool): Indicates if the user is disabled.
        uuid (str): A unique identifier for the user.
    """
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    uuid = Column(String, unique=True)