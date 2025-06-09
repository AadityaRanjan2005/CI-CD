from pydantic import BaseModel

class Token(BaseModel):
    """
    Class Task:
        Represents the structure of the authentication token returned to the user after successful login.
        This token is used by the client to authenticate future requests.

    Attributes:
        access_token (str): The JWT access token string that allows the user to access protected endpoints.
        token_type (str): The type of token issued (usually "bearer").
        user_uuid (str): The unique identifier of the authenticated user.
    """
    access_token: str
    token_type: str
    user_uuid: str

class TokenData(BaseModel):
    """
    Represents the data extracted from a JWT token, typically used to identify the user making a request.

    Attributes:
        username (str | None): The username of the authenticated user, or None if not present in the token.
    """
    username: str | None = None

class UserOut(BaseModel):
    """
    Represents the public user profile information returned by the API.

    Attributes:
        username (str): The user's unique username.
        full_name (str | None): The user's full name, if provided.
        email (str | None): The user's email address, if provided.
        disabled (bool | None): Indicates if the user's account is disabled.
        uuid (str): The unique identifier for the user.
    """
    username: str
    full_name: str | None = None
    email: str | None = None
    disabled: bool | None = None
    uuid: str
