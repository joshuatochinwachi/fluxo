import logging
import uuid
from fastapi import APIRouter,WebSocket,WebSocketDisconnect,HTTPException
from tasks.agent_tasks import onchain_task
from tasks.agent_tasks.onchain_task import protocol_task
from api.models.schemas import APIResponse

from celery.result import AsyncResult
from core import celery_app
from core.pubsub.channel_manager import ChannelNames
from models.redis_connect import db_connector

router = APIRouter()
redis_connect = db_connector(max_connections=5)
redis_db = redis_connect.get_connection()

smart_money_session : dict[str, WebSocket] = {}

logger = logging.getLogger(__name__)

@router.get('/')
async def onchain():
    task = onchain_task.delay() # adding the background worker
    # logic
    return {'agent':'onchain ','task_id': task.id}

    


@router.get('/protocols')
async def protocols():
    task = protocol_task.delay() # adding the background worker
    # logic
    return APIResponse(
        success=True,
        message=f'Mantle Protocol Loading For ',
        data={
            'task_id':task.id,
            'check_status':f"/onchain/status/{task.id}"
        }
    )


@router.websocket('/smart_money')
async def whale_whatcher(websocket: WebSocket):
    print("🦈 New Whale Watcher Connection Request Received")
    """
        Wesbsocket Route to stream smart transfer events in real-time
    """

    await websocket.accept()
    session_id = str(uuid.uuid4())

    smart_money_session[session_id] = websocket
    
    try:
        while True:
            # You can handle messages from the user if needed
            data = await websocket.receive_text()
            print(f"📩 Whale Subscrption Accepted {session_id}: {data}")

    except WebSocketDisconnect:
        # Clean up when user disconnects
        del smart_money_session[session_id]
        print(f"❌ User disconnected: {session_id}")


# This function listens to Redis channel and forwards messages to connected websockets
async def user_subscribed_tokens_update():
    print("🔔 Starting smart Transfer Listener...")
    pubsub = redis_db.pubsub()
    await pubsub.subscribe(ChannelNames.SMART_MONEY.value)

    async for message in pubsub.listen():
        if message['type'] == 'message':
            data = message['data']
            # Match data for whale transfer pattern
            # If metched Return data
            for session_id, websocket in smart_money_session.items():
                try:
                    await websocket.send_text(data)
                except Exception as e:
                    print(f"Error sending message to {session_id}: {e}")
                    continue


@router.get('/transactions')
async def user_transactions(wallet_address:str):
    from tasks.agent_tasks.onchain_task import fetch_transaction
    # from agents.onchain_agent import onchain_agent
    # onchain = onchain_agent()
    # if not wallet_address:
    #     return {}
    
    # task = (wallet_address)
    task = fetch_transaction.delay(wallet_address)
    return APIResponse(
        success=True,
        message=f'Fetch Transactions For {wallet_address}',
        data={
            'task_id':task.id,
            # 'result': await onchain.retrieve_transcton_from_db(wallet_address)
            'check_status':f"/onchain/status/{task.id}"
        }
    )


# Fetching onchain results
@router.get('/status/{task_id}')
async def get_onchain_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.ready():
            return APIResponse(
                success=True,
                message='Task completed',
                data={
                    'task_id': task_id,
                    'status': 'completed',
                    'result': task_result.result
                }
            )
        elif task_result.failed():
            return APIResponse(
                success=False,
                message='Task failed',
                data={
                    'task_id': task_id,
                    'status': 'failed',
                    'error': str(task_result.info)
                }
            )
        else:
            return APIResponse(
                success=True,
                message='Task in progress',
                data={
                    'task_id': task_id,
                    'status': 'processing',
                    'message': 'Transaction  fetching in progress...'
                }
            )
    except Exception as e:
        logger.error(f"Failed to get task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



