import logging
import asyncio
import json
import aiohttp
from Redis import ensure_system_message, append_history, get_history
from fastapi import WebSocket
import os
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

async def generate_with_ollama(uuid, session_id, websocket: WebSocket):
    """
    Generate a response using the Ollama API with the full conversation history for the given session ID.
    Args:
        session_id (str): The unique session ID for the conversation.
        websocket: The WebSocket connection to send messages back to the client.
        conversation_histories (dict): Dictionary containing conversation histories keyed by session ID.
        OLLAMA_URL (str): The URL of the Ollama API endpoint.
        MODEL_NAME (str): The name of the model to use for generation.
    """
    """Returns: None By default"""
    """sends the JSON response to the websocket connection""" 
    await ensure_system_message(uuid, session_id)
    history = await get_history(uuid, session_id)
    payload = {
        "model": MODEL_NAME,
        "messages": history,
        "stream": True
    }
    full_response = ""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_URL, json=payload) as resp:
                async for line in resp.content:
                    if not line or line == b"\n":
                        continue
                    try:
                        data = json.loads(line.decode("utf-8"))
                        chunk = data.get("message", {}).get("content", "")
                        full_response += chunk
                        await websocket.send_json({
                            "type": "response_chunk",
                            "content": chunk
                        })
                    except Exception as e:
                        logger.error(f"Error parsing Ollama chunk: {e}")
                await append_history(uuid, session_id, "assistant", full_response)
                await websocket.send_json({"type": "response_end"})
                logger.info(f"Model response completed: uuid={uuid}, session_id={session_id}")
    except asyncio.CancelledError:
        # Save the partial answer so far!
        if full_response.strip():
            await append_history(uuid, session_id, "assistant", full_response)
            logger.info(f"Model response stopped and partial saved: uuid={uuid}, session_id={session_id}")
        await websocket.send_json({"type": "stopped"})
    except Exception as e:
        logger.error(f"Error in generate_with_ollama: {e}")
        await websocket.send_json({"type": "error", "content": str(e)})