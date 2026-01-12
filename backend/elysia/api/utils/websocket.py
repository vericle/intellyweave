import asyncio
import time

import psutil
from typing import Callable, Any
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect, WebSocketState

# Logging
from elysia.api.core.log import logger

# Objects
from elysia.api.utils.default_payloads import error_payload


async def safe_websocket_send(websocket: WebSocket, data: Any) -> bool:
    """
    Safely send data through WebSocket with connection state checking.

    Args:
        websocket: The WebSocket connection
        data: Data to send (will be JSON serialized)

    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        # Check if WebSocket is still connected
        client_state = getattr(websocket, 'client_state', None)
        if client_state is not None and client_state != WebSocketState.CONNECTED:
            logger.debug(f"WebSocket not connected (state: {client_state}), skipping send")
            return False

        await websocket.send_json(data)
        return True

    except RuntimeError as e:
        if "websocket.send" in str(e).lower() or "already closed" in str(e).lower():
            logger.debug(f"WebSocket already closed, skipping send: {e}")
        else:
            logger.warning(f"RuntimeError sending WebSocket message: {e}")
        return False

    except Exception as e:
        logger.warning(f"Error sending WebSocket message: {e}")
        return False


async def help_websocket(websocket: WebSocket, ws_route: Callable):
    memory_process = psutil.Process()
    # initial_memory = memory_process.memory_info().rss
    try:
        await websocket.accept()
        while True:
            try:
                # start_time = time.time()
                # Wait for a message from the client
                # logger.info(f"Memory usage before receiving: {psutil.Process().memory_info().rss / 1024 / 1024}MB")
                try:
                    data = None
                    last_communication = time.time()

                    # Custom timeout handler
                    while True:
                        if time.time() - last_communication > 60:
                            # logger.warning("No communication for 60 seconds - sending heartbeat")
                            await safe_websocket_send(websocket, {"type": "heartbeat"})
                            last_communication = time.time()

                        try:
                            # Use a short timeout for receive_json to allow checking the timer
                            data = await asyncio.wait_for(
                                websocket.receive_json(), timeout=1.0
                            )
                            last_communication = time.time()

                            # Process the received data
                            await ws_route(data, websocket)
                            last_communication = (
                                time.time()
                            )  # Update timer after processing

                            # Check if it's a disconnect request
                            if data.get("type") == "disconnect":
                                return

                        except asyncio.TimeoutError:
                            continue

                except Exception as e:
                    error_str = str(e)
                    # WebSocket close code 1001 means "going away" - normal disconnect (e.g., page reload)
                    # Don't log this as an error since it's expected behavior
                    if "(1001," in error_str or "1001" in error_str:
                        logger.debug(f"WebSocket closed normally (going away): {error_str}")
                        break
                    error = error_payload(text=error_str, conversation_id="", query_id="")
                    await safe_websocket_send(websocket, error)
                    logger.error(f"Error in websocket communication: {error_str}")
                    break  # Exit the loop on communication error to prevent infinite loop

                # logger.info(f"Memory usage after receiving: {psutil.Process().memory_info().rss / 1024 / 1024}MB")
                # logger.info(f"Processing time: {time.time() - start_time}s")

            except WebSocketDisconnect:
                # logger.info("WebSocket disconnected", exc_info=True)
                break  # Exit the loop on disconnect

            except RuntimeError as e:
                if (
                    "Cannot call 'receive' once a disconnect message has been received"
                    in str(e)
                ):
                    # logger.info("WebSocket already disconnected")
                    break  # Exit the loop if the connection is already closed
                else:
                    raise  # Re-raise other RuntimeErrors

            except Exception as e:
                logger.error(f"Error in WebSocket: {str(e)}")
                if data and "conversation_id" in data and "query_id" in data:
                    error = error_payload(
                        text=str(e),
                        conversation_id=data["conversation_id"],
                        query_id=data["query_id"],
                    )
                    await safe_websocket_send(websocket, error)
                elif data and "conversation_id" in data:
                    error = error_payload(
                        text=str(e),
                        conversation_id=data["conversation_id"],
                        query_id="",
                    )
                    await safe_websocket_send(websocket, error)
                else:
                    error = error_payload(
                        text=str(e), conversation_id="", query_id=""
                    )
                    await safe_websocket_send(websocket, error)

                break  # Exit the loop after attempting to send the error message

    except Exception as e:
        logger.warning(f"Closing WebSocket: {str(e)}")
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            logger.info("WebSocket already closed")
