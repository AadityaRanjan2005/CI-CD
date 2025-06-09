
from auth import authenticate_user, create_access_token, get_current_user
from database import get_db
from sqlalchemy.orm import Session
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, JSONResponse
import logging      
from Schemas import Token, UserOut        
from datetime import timedelta
from dotenv import load_dotenv
import os
from database import  engine, get_db
from models import Base, User
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from ConnectionManager import ConnectionManager
from uuid import uuid4
import json
from Redis import ensure_system_message, get_all_sessions, append_history, get_history
from ollama_chat import generate_with_ollama
import asyncio
from fastapi.staticfiles import StaticFiles



# Logging setup 
logger = logging.getLogger(__name__)

# # Load environment variables
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter()

router.mount("/static", StaticFiles(directory="static"), name="static")

manager = ConnectionManager()


@router.on_event("startup")
def startup_event():
    """
    Initialise the database on startup.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Function Task:
        Authenticates the user and returns an access token if the credentials are correct.

    Arguments:
        form_data (OAuth2PasswordRequestForm): The form containing username and password.
        db (Session): The database session to use for the query.

    Returns:
        dict: Contains the access token, token type, and user UUID.

    Raises:
        HTTPException: If the username or password is incorrect.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.info(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    logger.info(f"User logged in: {user.username} (uuid: {user.uuid})")
    return {"access_token": access_token, "token_type": "bearer", "user_uuid": user.uuid}

@router.get("/users/me/", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Function Task:
        Returns the profile information of the currently authenticated user.

    Arguments:
        current_user (User): The user object for the currently authenticated user.

    Returns:
        User: The user profile information.
    """
    logger.info(f"User profile accessed: {current_user.username}")
    return current_user

@router.websocket("/api/chat")
async def websocket_endpoint(websocket: WebSocket, uuid: str = Query(...), session_id: str = Query(None)):
    """ Handle WebSocket connections for chat sessions.
    This function manages the WebSocket connection, handles incoming messages,
    and interacts with the Ollama API to generate responses based on conversation history."""
    """Manages the WebSocket connection lifecycle,
    Receives and processes messages,
    Starts and stops background tasks,
    Sends responses to the client via the WebSocket,
    Handles exceptions and cleans up resources."""
    if not session_id:
        session_id = str(uuid4())
    await ensure_system_message(uuid, session_id)
    try:
        await manager.connect(websocket, session_id)
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "user_message":
                    manager.stop_task(session_id)
                    await append_history(uuid, session_id, "user", message["content"])
                    logger.info(f"User message received: uuid={uuid}, session_id={session_id}")
                    task = asyncio.create_task(
                        generate_with_ollama(uuid, session_id, websocket)
                    )
                    manager.set_task(session_id, task)
                elif message.get("type") == "stop_generation":
                    stopped = manager.stop_task(session_id)
                    if stopped:
                        await manager.send_message({"type": "stopped"}, session_id)
                        logger.info(f"Stop requested by user: uuid={uuid}, session_id={session_id}")
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON on WebSocket")
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocketDisconnect: session_id={session_id}")
    except Exception as e:
        manager.disconnect(session_id)
        logger.error(f"WebSocket error: {e}")


@router.get("/")
def serve_index():
    """
    Function Task:
        Serves the main index HTML page to the client.

    Arguments:
        None

    Returns:
        FileResponse: The index.html file from the static directory.
    """
    # Redirect to login page
    return FileResponse("static/index.html")

@router.get("/chat.html")
def serve_chat():
    """
    Function Task:
        Serves the chat HTML page to the client.

    Arguments:
        None

    Returns:
        FileResponse: The chat.html file from the static directory.
    """
    return FileResponse("static/chat.html")


@router.get("/history_sessions")
async def history_sessions(uuid: str):
    """
    Function Task:
        Returns a list of all chat sessions for a user.

    Arguments:
        uuid (str): The user's unique identifier.

    Returns:
        list: A list of session metadata dictionaries.
    """
    sessions = await get_all_sessions(uuid)
    logger.info(f"History sessions fetched for uuid={uuid}")
    return sessions

@router.get("/history/{session_id}")
async def get_history_api(session_id: str, uuid: str):
    """
    Function Task:
        Returns the chat history for a specific session and user.

    Arguments:
        session_id (str): The chat session's unique identifier.
        uuid (str): The user's unique identifier.

    Returns:
        JSONResponse: The chat history for the session.
    """
    history = await get_history(uuid, session_id)
    logger.info(f"History fetched: uuid={uuid}, session_id={session_id}")
    return JSONResponse(content={"session_id": session_id, "history": history})