from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis
import asyncio
import json
from typing import Dict
from app.config import Settings

router = APIRouter()

settings = Settings()

redis_client = redis.Redis(
    username=settings.redis_username,
    host=settings.redis_hostname, 
    port=settings.redis_port, 
    password=settings.redis_password,
    db=0,
    decode_responses=True)

USER_QUEUE = "user_connection_queue"
CHAT_CHANNEL_PREFIX = "chat_"
active_connections: Dict[str, WebSocket] = {}
user_partners: Dict[str, str] = {}

async def match_users():
    while True:
        if redis_client.llen(USER_QUEUE) >= 2:
            user1 = redis_client.rpop(USER_QUEUE)
            user2 = redis_client.rpop(USER_QUEUE)

            if user1 and user2:
                chat_channel = f"{CHAT_CHANNEL_PREFIX}{user1}_{user2}"
                redis_client.set(user1, chat_channel)
                redis_client.set(user2, chat_channel)
                
                user_partners[user1] = user2
                user_partners[user2] = user1

                if user1 in active_connections:
                    await active_connections[user1].send_text(
                        json.dumps({"type": "matched", "chatPartner": user2})
                    )
                if user2 in active_connections:
                    await active_connections[user2].send_text(
                        json.dumps({"type": "matched", "chatPartner": user1})
                    )

        await asyncio.sleep(1)

@router.on_event("startup")
async def startup_event():
    asyncio.create_task(match_users())

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    active_connections[user_id] = websocket

    redis_client.lpush(USER_QUEUE, user_id)

    try:
        while True:
            data = await websocket.receive_text()

            chat_channel = redis_client.get(user_id)

            if not chat_channel:
                await websocket.send_text(json.dumps({"type": "info", "message": "Waiting for a match..."}))
                continue

            partner_id = user_partners.get(user_id)
            if partner_id and partner_id in active_connections:

                partner_ws = active_connections[partner_id]
                try:
                    await partner_ws.send_text(
                        json.dumps({
                            "type": "message",
                            "sender": user_id,
                            "content": data
                        })
                    )
                except Exception as e:
                    print(f"❌ Error sending to partner {partner_id}: {str(e)}")
            else:
                print(f"⚠️ Partner for {user_id} not found or not connected")

    except WebSocketDisconnect:
        partner_id = user_partners.get(user_id)
        if partner_id and partner_id in active_connections:
            try:
                await active_connections[partner_id].send_text(
                    json.dumps({
                        "type": "partner_disconnected", 
                        "message": "Your chat partner has disconnected"
                    })
                )
            except Exception as e:
                print(f"❌ Error notifying partner: {str(e)}")

        if user_id in active_connections:
            del active_connections[user_id]
        if user_id in user_partners:
            del user_partners[user_id]
        redis_client.delete(user_id)