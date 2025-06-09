import redis.asyncio as redis
import json
import time
import logging
import os
from dotenv import load_dotenv

# Logging setup 
logger = logging.getLogger(__name__)


load_dotenv()

# --- Chat/History/WS Logic ---
REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def session_key(uuid, session_id):
    """
    Function Task:
        Creates a unique key for storing chat history in Redis for a specific user and session.

    Arguments:
        uuid (str): The user's unique identifier.
        session_id (str): The chat session's unique identifier.

    Returns:
        str: The Redis key for the chat history.
    """
    return f"chat:{uuid}:{session_id}"

def session_meta_key(uuid, session_id):
    """
    Function Task:
        Creates a unique key for storing chat session metadata in Redis.

    Arguments:
        uuid (str): The user's unique identifier.
        session_id (str): The chat session's unique identifier.

    Returns:
        str: The Redis key for the chat session metadata.
    """
    return f"chatmeta:{uuid}:{session_id}"

async def append_history(uuid, session_id, role, content):
    """
    Function Task:
        Adds a new message to the chat history in Redis and updates session metadata.

    Arguments:
        uuid (str): The user's unique identifier.
        session_id (str): The chat session's unique identifier.
        role (str): The role of the sender ('user', 'assistant', or 'system').
        content (str): The message content.

    Returns:
        None
    """
    entry = {
        "role": role,
        "content": content,
        "timestamp": int(time.time())
    }
    await redis_client.rpush(session_key(uuid, session_id), json.dumps(entry))
    meta = await redis_client.hgetall(session_meta_key(uuid, session_id))
    if role == "user":
        await redis_client.hset(session_meta_key(uuid, session_id), mapping={
            "session_id": session_id,
            "title": content[:32] if not meta.get("title") else meta["title"],
            "preview": content[:64],
            "updated_at": str(int(time.time()))
        })
    elif role == "assistant":
        await redis_client.hset(session_meta_key(uuid, session_id), mapping={
            "session_id": session_id,
            "preview": content[:64],
            "updated_at": str(int(time.time()))
        })
    logger.info(f"History appended: uuid={uuid}, session_id={session_id}, role={role}")

async def get_history(uuid, session_id):
    """
    Function Task:
        Retrieves the chat history for a specific user and session from Redis.

    Arguments:
        uuid (str): The user's unique identifier.
        session_id (str): The chat session's unique identifier.

    Returns:
        list: A list of message entries for the session.
    """
    entries = await redis_client.lrange(session_key(uuid, session_id), 0, -1)
    return [json.loads(e) for e in entries]

async def ensure_system_message(uuid, session_id):
    """
    Function Task:
        Makes sure the first message in a chat session is a system prompt.

    Arguments:
        uuid (str): The user's unique identifier.
        session_id (str): The chat session's unique identifier.

    Returns:
        None
    """
    if await redis_client.llen(session_key(uuid, session_id)) == 0:
        await append_history(uuid, session_id, "system", "You are a helpful assistant.")

async def get_all_sessions(uuid):
    """
    Function Task:
        Retrieves all chat session metadata for a user from Redis.

    Arguments:
        uuid (str): The user's unique identifier.

    Returns:
        list: A list of session metadata dictionaries, sorted by last updated.
    """
    keys = await redis_client.keys(f"chatmeta:{uuid}:*")
    sessions = []
    for key in keys:
        meta = await redis_client.hgetall(key)
        if meta:
            sessions.append(meta)
    sessions.sort(key=lambda x: int(x.get("updated_at", "0")), reverse=True)
    return sessions

