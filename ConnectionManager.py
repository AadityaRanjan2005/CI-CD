import asyncio
from typing import Dict
from fastapi import WebSocket
import logging



logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages active websockest connections and associated backgorund tasks for each session.
      
    Attributes: 
        active_connections (dict): A dictionary mapping session IDs to active WebSocket connections.
        generation_tasks (dict): A dictionary mapping session IDs to asyncio tasks for ongoing generation processes.
    """
    
    def __init__(self):
        """Initialize the connection manager with empty dictionaries for active connections and generation tasks."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.generation_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept the new websocket connection and store in the active_connections dictionary."""
        """ARGS: 
                websocket: the websocket connection 
                session_id (str): the unique session ID.
              """
        """Returns: None if the session_id is already in the active_connections dictionary, it does nothing."""
        """Accepts a new WebSocket connection and stores it in the active_connections dictionary."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        await websocket.send_json({
            "type": "session_id",
            "session_id": session_id
        })
        logger.info(f"WebSocket connected: session_id={session_id}")

    def disconnect(self, session_id: str):
        """ Remove the websocket connection from the dictionarry of active_Connections """
        """ARGS: session_id : the uniques session ID """
        """Returns: None if the session_id is not in the active_connections dictionary, it does nothing."""
        """Remove the websocket connection for the given session ID and cancel any ongoing generation task."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        task = self.generation_tasks.pop(session_id, None)
        if task and not task.done():
            task.cancel()
        logger.info(f"WebSocket disconnected: session_id={session_id}")

    async def send_message(self, message: dict, session_id: str):
        """Send a json message to the specified websocket connection (at the user end)"""
        """ARGS
        message : the message to sent the user
        session_id : guide which websocket connection to send the message to
        """
        """Returns: None if the session_id is not in the active_connections dictionary, it does nothing."""
        """Sends a JSON message to the WebSocket connection associated with the given session ID."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

    def set_task(self, session_id: str, task: asyncio.Task):
        """ set the asyncio task for the specific session ID to manage ongoing generation processes."""
        """ARGS: session_id : the unique session ID for the websocket connection
                task: we give the asyncio task to manage the users chat generation process"""
        """Returns: None  it stores the given asyncio task in the generation_tasks dictionary with the session_id as the key."""
        self.generation_tasks[session_id] = task

    def stop_task(self, session_id: str):
        """ Stop the generation task for the specified session ID if it exists and is running."""
        """ARGS: session_id : the unique session ID for the websocket connection"""
        """Returns: True if the task was found and stopped, False otherwise."""
        task = self.generation_tasks.get(session_id)
        if task and not task.done():
            task.cancel()
            logger.info(f"Generation task stopped: session_id={session_id}")
            return True
        return False