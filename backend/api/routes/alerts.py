"""
Alert API Routes
Endpoints for retrieving and managing alerts
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from api.models.alerts import Alert
from api.models.schemas import APIResponse
from tasks.alert_coordinator import coordinate_alerts, batch_alert_processing
from tasks.periodic_tasks import periodic_portfolio_monitoring
from celery.result import AsyncResult
from core import celery_app
from core.config import get_redis_connection 

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize alert manager (in production, use dependency injection)


@router.get("/alerts")
async def get_alerts(
    wallet_address: Optional[str] = Query(None, description="Filter by wallet address"),
    limit: int = Query(50, ge=1, le=100, description="Number of alerts to return")
):
    """
    Get alerts for a user
    
    Query params:
    - wallet_address: Optional filter by wallet
    - limit: Max number of alerts (default 50)
    """
    from services.alert_manager import AlertManager
    alert_manager = AlertManager()
    try:
        alerts = await alert_manager.get_alerts(wallet_address, limit)
        print(alerts)
        return APIResponse(
            success=True,
            message=f"Retrieved {len(alerts)} alerts",
            data={
                'wallet_address':wallet_address,
                "alerts": [alert for alert in alerts]
            }
        )
    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/undelivered")
async def get_undelivered_alerts(
    wallet_address:str
):
    """
    Get all undelivered alerts (for x402 delivery service)
    """
    
    from services.alert_manager import AlertManager
    alert_manager = AlertManager()
    try:
        alerts = await alert_manager.get_undelivered_alerts(wallet_address)
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(alerts)} undelivered alerts",
            data={
                "alerts": [alert for alert in alerts],
                "total": len(alerts)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-delivered/{alert_id}")
async def mark_alert_delivered(
    alert_id: str,
    wallet_address:str,
    delivery_method: str = Query(..., description="Delivery method used")
):
    """
    Mark an alert as delivered
    Used by x402 delivery service after successful delivery
    """

    
    from services.alert_manager import AlertManager
    alert_manager = AlertManager()
    try:
        await alert_manager.mark_delivered(alert_id, delivery_method, wallet_address)
        
        return APIResponse(
            success=True,
            message="Alert marked as delivered",
            data={"alert_id": alert_id, "delivery_method": delivery_method}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/coordinate')
async def trigger_alert_coordination(
    wallet_address: str,
    analysis_types: Optional[List[str]] = Query(None, description="Types: risk, social, macro, execution")
):
    """
    Coordinate multi-agent analysis with consolidated alerts
    
    Example:
    POST /alerts/coordinate?wallet_address=0x123...&analysis_types=risk&analysis_types=social
    """
    try:
        task = coordinate_alerts.delay(wallet_address, analysis_types)
        
        return APIResponse(
            success=True,
            message='Alert coordination started',
            data={
                'task_id': task.id,
                'wallet_address': wallet_address,
                'analysis_types': analysis_types or ['risk', 'social', 'macro'],
                'check_status': f'/api/v1/alerts/task-status/{task.id}'
            }
        )
    except Exception as e:
        logger.error(f"Failed to start alert coordination: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/batch')
async def trigger_batch_alerts(
    wallet_addresses: List[str] = Query(..., description="List of wallet addresses")
):
    """
    Process alerts for multiple wallets
    
    Example:
    POST /alerts/batch?wallet_addresses=0x123...&wallet_addresses=0x456...
    """
    try:
        task = batch_alert_processing.delay(wallet_addresses)
        
        return APIResponse(
            success=True,
            message=f'Batch alert processing started for {len(wallet_addresses)} wallets',
            data={
                'task_id': task.id,
                'wallets_count': len(wallet_addresses),
                'check_status': f'/api/v1/alerts/task-status/{task.id}'
            }
        )
    except Exception as e:
        logger.error(f"Failed to start batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/task-status/{task_id}')
async def get_alert_task_status(task_id: str):
    """
    Check status of alert coordination task
    """
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
                    'message': 'Alert coordination in progress...'
                }
            )
    except Exception as e:
        logger.error(f"Failed to get task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/track-wallet')
async def add_wallet_to_tracking(
    wallet_address: str = Query(..., description="Wallet address to track")
):
    """
    Add wallet to periodic monitoring (every 15 minutes)
    """
    try:
        redis_conn = get_redis_connection()
        # Add to tracked wallets set
        await redis_conn.sadd("tracked_wallets", wallet_address)
        
        # Get current count
        count = await redis_conn.scard("tracked_wallets")
        
        return APIResponse(
            success=True,
            message='Wallet added to monitoring',
            data={
                'wallet_address': wallet_address,
                'total_tracked': count,
                'monitoring_interval': '15 minutes',
                'next_check': 'Within 15 minutes'
            }
        )
    except Exception as e:
        logger.error(f"Failed to add wallet to tracking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/track-wallet')
async def remove_wallet_from_tracking(
    wallet_address: str = Query(..., description="Wallet address to stop tracking")
):
    """
    Remove wallet from periodic monitoring
    """
    try:
        redis_conn = get_redis_connection()
        
        
        # Remove from tracked wallets set
        removed = await redis_conn.srem("tracked_wallets", wallet_address)
        
        if removed:
            count = await redis_conn.scard("tracked_wallets")
            return APIResponse(
                success=True,
                message='Wallet removed from monitoring',
                data={
                    'wallet_address': wallet_address,
                    'total_tracked': count
                }
            )
        else:
            return APIResponse(
                success=False,
                message='Wallet was not being tracked',
                data={'wallet_address': wallet_address}
            )
    except Exception as e:
        logger.error(f"Failed to remove wallet from tracking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# checked
@router.get('/tracked-wallets')
async def get_tracked_wallets():
    """
    Get list of all wallets being monitored
    """
    try:
        redis_conn = get_redis_connection()
        
        
        tracked_wallets = await redis_conn.smembers("tracked_wallets")
        
        return APIResponse(
            success=True,
            message=f'Retrieved {len(tracked_wallets)} tracked wallets',
            data={
                'total_tracked': len(tracked_wallets),
                'wallets': list(tracked_wallets),
                'monitoring_interval': '15 minutes'
            }
        )
    except Exception as e:
        logger.error(f"Failed to get tracked wallets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/manual-monitoring')
async def trigger_manual_monitoring():
    print('start mannual')
    """
    Manually trigger monitoring of all tracked wallets (bypasses schedule)
    """
    try:
        task = periodic_portfolio_monitoring.delay()
        
        return APIResponse(
            success=True,
            message='Manual monitoring triggered',
            data={
                'task_id': task.id,
                'check_status': f'/api/v1/alerts/task-status/{task.id}'
            }
        )
    except Exception as e:
        logger.error(f"Failed to trigger manual monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def alerts_health():
    from services.alert_manager import AlertManager
    alert_manager = AlertManager()

    """Alert system health check"""
    total_alerts = len(alert_manager.alerts)
    undelivered = len(alert_manager.get_undelivered_alerts())
    
    return {
        "service": "alerts",
        "status": "operational",
        "version": "2.0_with_coordination",
        "stats": {
            "total_alerts": total_alerts,
            "undelivered": undelivered,
            "delivered": total_alerts - undelivered
        },
        "alert_types": [t.value for t in alert_manager.default_triggers.keys()],
        "features": [
            "Alert retrieval and management",
            "Multi-agent alert coordination",
            "Batch alert processing",
            "Periodic monitoring (15min intervals)",
            "Wallet tracking management",
            "Cross-agent alert consolidation",
            "x402 delivery integration"
        ],
        "endpoints": [
            "GET /alerts/ - Get alerts",
            "GET /alerts/undelivered - Get undelivered alerts",
            "POST /alerts/mark-delivered/{'alert_id'} - Mark alert as delivered",
            "POST /alerts/coordinate - Coordinate multi-agent alerts",
            "POST /alerts/batch - Batch process multiple wallets",
            "GET /alerts/task-status/{'task_id'} - Check task status",
            "POST /alerts/track-wallet - Add wallet to monitoring",
            "DELETE /alerts/track-wallet - Remove wallet from monitoring",
            "GET /alerts/tracked-wallets - List tracked wallets",
            "POST /alerts/manual-monitoring - Trigger manual check"
        ]
    }
