import uuid
from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from tasks.agent_tasks import onchain_task

from celery.result import AsyncResult
from core import celery_app
from models.redis_connect import db_connector

router = APIRouter()
redis_connect = db_connector(max_connections=5)
redis_db = redis_connect.get_connection()

active_sessions : dict[str, WebSocket] = {}

@router.get('/onchain')
async def onchain():
    task = onchain_task.delay() # adding the background worker
    # logic
    return {'agent':'onchain ','task_id': task.id}

# fetching the results
@router.get('/onchain/status/{task_id}')
async def get_onchain_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }

@router.websocket('/whale_watcher')
async def whale_whatcher(websocket: WebSocket):
    print("🦈 New Whale Watcher Connection Request Received")
    """
        Wesbsocket Route to stream Whale transfer events in real-time
    """

    await websocket.accept()
    session_id = str(uuid.uuid4())

    active_sessions[session_id] = websocket
    
    try:
        while True:
            # You can handle messages from the user if needed
            data = await websocket.receive_text()
            print(f"📩 Whale Subscrption Accepted {session_id}: {data}")

    except WebSocketDisconnect:
        # Clean up when user disconnects
        del active_sessions[session_id]
        print(f"❌ User disconnected: {session_id}")

# This function listens to Redis channel and forwards messages to connected websockets
async def user_subscribed_tokens_update():
    print("🔔 Starting Whale Transfer Listener...")
    pubsub = redis_db.pubsub()
    await pubsub.subscribe('token_watch_channel')

    async for message in pubsub.listen():
        if message['type'] == 'message':
            data = message['data']
            # Match data for whale transfer pattern
            # If metched Return data
            print('hello')
            for session_id, websocket in active_sessions.items():
                try:
                    await websocket.send_text(data)
                except Exception as e:
                    print(f"Error sending message to {session_id}: {e}")
                    continue




