"""
Alert Manager Service
Handles alert triggering, storage, and delivery coordination
"""
import asyncio
import json
import logging
import uuid

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from api.models.alerts import (
    Alert, AlertType, AlertSeverity, AlertTrigger, AlertRule
)
from core.config import get_redis_connection
logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manages alert lifecycle:
    1. Check if alert should trigger
    2. Create alert
    3. Store alert
    4. Queue for delivery
    """
    
    def __init__(self):
        # In-memory storage for Week 2 (Week 3: use Redis/DB)
        self.alerts: List[Alert] = []
        self.alert_history: Dict[str, List[datetime]] = {}
        
        self.user_alerts = 'USERS_ALERT'
    # Don't resolve the Redis connection at import time to avoid
    # circular imports; resolve lazily when first needed.
        self.redis_con = get_redis_connection()

            # Default alert triggers (based on Risk Agent thresholds)
        self.default_triggers = self._initialize_default_triggers()
        
        logger.info("AlertManager initialized")

    def _initialize_default_triggers(self) -> Dict[AlertType, AlertTrigger]:
        """
        Initialize default alert triggers based on Risk Agent thresholds
        Uses Kelvin's research and Electus's validation
        """
        return {
            # Risk score alerts
            AlertType.HIGH_RISK_SCORE: AlertTrigger(
                alert_type=AlertType.HIGH_RISK_SCORE,
                threshold=70.0,  # High risk level
                comparison="gte",
                cooldown_minutes=120  # 2 hours
            ),
            AlertType.CRITICAL_RISK_SCORE: AlertTrigger(
                alert_type=AlertType.CRITICAL_RISK_SCORE,
                threshold=85.0,  # Critical risk
                comparison="gte",
                cooldown_minutes=60  # 1 hour - more urgent
            ),
            
            # Concentration alerts
            AlertType.CONCENTRATION_WARNING: AlertTrigger(
                alert_type=AlertType.CONCENTRATION_WARNING,
                threshold=60.0,  # High concentration (from Risk Agent)
                comparison="gte",
                cooldown_minutes=180  # 3 hours
            ),
            
            # Liquidity alerts
            AlertType.LIQUIDITY_RISK: AlertTrigger(
                alert_type=AlertType.LIQUIDITY_RISK,
                threshold=60.0,  # Low liquidity score
                comparison="gte",
                cooldown_minutes=240  # 4 hours
            ),
            
            # Contract risk alerts
            AlertType.CONTRACT_RISK: AlertTrigger(
                alert_type=AlertType.CONTRACT_RISK,
                threshold=40.0,  # Significant contract exposure
                comparison="gte",
                cooldown_minutes=360  # 6 hours
            ),
            
            # Market stress alerts (from Kelvin's correlation hypothesis)
            AlertType.MARKET_STRESS: AlertTrigger(
                alert_type=AlertType.MARKET_STRESS,
                threshold=70.0,  # High correlation risk
                comparison="gte",
                cooldown_minutes=120  # 2 hours
            ),
        }
    
    async def check_risk_alerts(
        self, 
        wallet_address: str,
        risk_score: float,
        risk_factors: Dict[str, float],
        market_condition: str
    ) -> List[Alert]:
        """
        Check if any risk-based alerts should be triggered
        
        Args:
            wallet_address: User's wallet
            risk_score: Overall risk score (0-100)
            risk_factors: Individual factor scores
            market_condition: Current market condition
        
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        # Check overall risk score
        if risk_score :#>= 85:
            alert = self._create_critical_risk_alert(
                wallet_address, risk_score, risk_factors
            )
            if alert:
                print('Critical trigger')
                triggered_alerts.append(alert)
                
        elif risk_score :#>= 70:
            alert = self._create_high_risk_alert(
                wallet_address, risk_score, risk_factors
            )
            if alert:
                print('Critical 2 trigger')
                triggered_alerts.append(alert)
        
        # Check concentration
        concentration = risk_factors.get("concentration", 0)
        if concentration :#>= 60:
            alert = self._create_concentration_alert(
                wallet_address, concentration
            )
            if alert:
                print('Critical 3trigger')
                triggered_alerts.append(alert)
        
        # Check liquidity
        liquidity = risk_factors.get("liquidity", 0)
        if liquidity:# >= 60:
            alert = self._create_liquidity_alert(
                wallet_address, liquidity
            )
            if alert:
                print('Critical 4 trigger')
                triggered_alerts.append(alert)
        
        # Check contract risk
        contract_risk = risk_factors.get("contract_risk", 0)
        if contract_risk :#>= 40:
            alert = self._create_contract_risk_alert(
                wallet_address, contract_risk
            )
            if alert:
                print('Critical 5 trigger')
                triggered_alerts.append(alert)
        
        # Check market stress (correlation risk)
        correlation_risk = risk_factors.get("correlation_risk", 0)
        if correlation_risk :#>= 70 or market_condition == "stressed_correlation":
            alert = self._create_market_stress_alert(
                wallet_address, correlation_risk, market_condition
            )
            if alert:
                
                print('Critical 6 trigger')
                triggered_alerts.append(alert)
        
       
        
        logger.info(f"Checked risk alerts for {wallet_address}: {len(triggered_alerts)} triggered")
       
        return triggered_alerts
    
    def _create_critical_risk_alert(
        self, 
        wallet_address: str, 
        risk_score: float,
        factors: Dict[str, float]
    ) -> Optional[Alert]:
        """Create critical risk score alert"""
        
        # Check cooldown
        alert_key = f"{wallet_address}:critical_risk"
        if not self._check_cooldown(alert_key, 60):
            return None
        
        # Find main risk driver
        max_factor = max(factors.items(), key=lambda x: x[1])
        
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.CRITICAL_RISK_SCORE,
            severity=AlertSeverity.CRITICAL,
            title="🚨 Critical Portfolio Risk Detected",
            message=(
                f"Your portfolio risk score is CRITICAL at {risk_score:.1f}/100. "
                f"Primary concern: {max_factor[0].replace('_', ' ').title()} ({max_factor[1]:.1f}). "
                f"Immediate action recommended to reduce exposure."
            ),
            wallet_address=wallet_address,
            current_value=risk_score,
            threshold=85.0,
            details={
                "risk_scoree":risk_score,
                "risk_factors": factors,
                "main_driver": max_factor[0],
                "action": "immediate_rebalance_required"
            },
            triggered_by="risk_agent"
        )
        
        self._update_cooldown(alert_key)
        return alert
    
    def _create_high_risk_alert(
        self,
        wallet_address: str,
        risk_score: float,
        factors: Dict[str, float]
    ) -> Optional[Alert]:
        """Create high risk score alert"""
        
        alert_key = f"{wallet_address}:high_risk"
        # if not self._check_cooldown(alert_key, 120):
        #     return None
        
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.HIGH_RISK_SCORE,
            severity=AlertSeverity.HIGH,
            title="⚠ High Portfolio Risk",
            message=(
                f"Your portfolio risk score is HIGH at {risk_score:.1f}/100. "
                f"Consider reviewing your holdings and rebalancing to reduce risk exposure."
            ),
            wallet_address=wallet_address,
            current_value=risk_score,
            threshold=70.0,
            details={"risk_factors": factors},
            triggered_by="risk_agent"
        )
        
        self._update_cooldown(alert_key)
        return alert
    
    def _create_concentration_alert(
        self,
        wallet_address: str,
        concentration_score: float
    ) -> Optional[Alert]:
        """Create concentration warning alert"""
        
        alert_key = f"{wallet_address}:concentration"
        # if not self._check_cooldown(alert_key, 180):
        #     return None
        
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.CONCENTRATION_WARNING,
            severity=AlertSeverity.WARNING,
            title="📊 High Concentration Risk",
            message=(
                f"Portfolio concentration is {concentration_score:.1f}/100. "
                f"Your holdings are heavily concentrated in few assets. "
                f"Diversifying into 3-5 assets can reduce risk significantly."
            ),
            wallet_address=wallet_address,
            current_value=concentration_score,
            threshold=60.0,
            details={"recommendation": "diversify_holdings"},
            triggered_by="risk_agent"
        )
        
        self._update_cooldown(alert_key)
        return alert
    
    def _create_liquidity_alert(
        self,
        wallet_address: str,
        liquidity_score: float
    ) -> Optional[Alert]:
        """Create liquidity risk alert"""
        
        alert_key = f"{wallet_address}:liquidity"
        # if not self._check_cooldown(alert_key, 240):
        #     return None
        
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.LIQUIDITY_RISK,
            severity=AlertSeverity.WARNING,
            title="💧 Liquidity Risk Detected",
            message=(
                f"Portfolio liquidity risk is {liquidity_score:.1f}/100. "
                f"Some assets may have limited liquidity on Mantle DEXs. "
                f"Consider moving to higher liquidity protocols like Merchant Moe or FusionX."
            ),
            wallet_address=wallet_address,
            current_value=liquidity_score,
            threshold=60.0,
            details={"action": "move_to_liquid_dexs"},
            triggered_by="risk_agent"
        )
        
        self._update_cooldown(alert_key)
        return alert
    
    def _create_contract_risk_alert(
        self,
        wallet_address: str,
        contract_risk_score: float
    ) -> Optional[Alert]:
        """Create contract risk alert"""
        
        alert_key = f"{wallet_address}:contract_risk"
        # if not self._check_cooldown(alert_key, 360):
        #     return None
        
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.CONTRACT_RISK,
            severity=AlertSeverity.WARNING,
            title="🔒 Smart Contract Risk Exposure",
            message=(
                f"Contract risk score is {contract_risk_score:.1f}/100. "
                f"You have exposure to emerging or unaudited protocols. "
                f"Review audit status and consider established alternatives."
            ),
            wallet_address=wallet_address,
            current_value=contract_risk_score,
            threshold=40.0,
            details={"action": "review_protocol_safety"},
            triggered_by="risk_agent"
        )
        
        self._update_cooldown(alert_key)
        return alert
    
    def _create_market_stress_alert(
        self,
        wallet_address: str,
        correlation_risk: float,
        market_condition: str
    ) -> Optional[Alert]:
        """Create market stress alert (Kelvin's correlation hypothesis)"""
        
        alert_key = f"{wallet_address}:market_stress"
        # if not self._check_cooldown(alert_key, 120):
        #     return None
        
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.MARKET_STRESS,
            severity=AlertSeverity.HIGH,
            title="🌊 Market Stress Detected",
            message=(
                f"Market correlation is elevated ({correlation_risk:.1f}/100), "
                f"indicating {market_condition.replace('_', ' ')}. "
                f"High correlation periods often signal fear or herd behavior. "
                f"Consider reducing overall risk exposure or increasing stablecoin allocation."
            ),
            wallet_address=wallet_address,
            current_value=correlation_risk,
            threshold=70.0,
            details={
                "market_condition": market_condition,
                "hypothesis": "kelvins_macro_correlation",
                "action": "reduce_risk_exposure"
            },
            triggered_by="risk_agent"
        )
        
        self._update_cooldown(alert_key)
        return alert
    
    def _check_cooldown(self, alert_key: str, cooldown_minutes: int) -> bool:
        """Check if alert is past cooldown period"""
        if alert_key not in self.alert_history:
            return True
        
        last_triggered = self.alert_history[alert_key][-1]
        time_since = (datetime.utcnow() - last_triggered).total_seconds() / 60
        print('alertt checking Cool Down',alert_key)
        return time_since >= cooldown_minutes
    
    def _update_cooldown(self, alert_key: str):
        """Update cooldown tracking"""
        if alert_key not in self.alert_history:
            self.alert_history[alert_key] = []
        
        self.alert_history[alert_key].append(datetime.utcnow())
        
        # Keep only last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.alert_history[alert_key] = [
            t for t in self.alert_history[alert_key] if t > cutoff
        ]
    
    def _store_alert(self, alert: Alert):
        """Store alert (in-memory for now)"""
        self.alerts.append(alert)
        logger.info(f"Stored alert: {alert.alert_type.value} for {alert.wallet_address}")
    
    async def get_alerts(
        self,
        wallet_address: Optional[str] = None,
        limit: int = 50
    ) -> List[Alert]:
        """Retrieve alerts"""
        if wallet_address:
            stored_alert_data = await self.retrieve_alert(wallet_address)
            alerts =  stored_alert_data.get('alerts')
        else:
            alerts = [None]
        
        # for a in alerts:
        #     print(type(a))
        return sorted(alerts, key=lambda a: a['timestamp'], reverse=True)[:limit]
    
    async def get_undelivered_alerts(self,wallet_address:str) -> List[Alert]:
        """Get alerts pending delivery"""
        stored_alert_data = await self.retrieve_alert(wallet_address)
        alerts =  stored_alert_data.get('alerts')
        undelivered_alert = []
        for alert in alerts:
            if not alert['delivered']:
                undelivered_alert.append(alert)

        return undelivered_alert
    
    async def mark_delivered(self, alert_id: str, delivery_method: str,wallet_address:str):
        """Mark alert as delivered"""
        from api.models.alerts import Alert

        stored_alert_data = await self.retrieve_alert(wallet_address)
        alerts =  stored_alert_data.get('alerts')
        update_alert_status = []
        for alert in alerts:
            if alert.get('alert_id') == alert_id:
                print('there is an alert id')
                alert['delivered'] = True
                alert['delivery_method'] = delivery_method
                logger.info(f"Alert {alert_id} marked as delivered via {delivery_method}")
               
            
            update_alert_status.append(alert)
        self.store_alert(update_alert_status,wallet_address)
        print('Updated Alert Delivery Status!')


    def store_alert(self,all_alerts:list|dict,wallet_address:str):
        alert_data = { 
        'wallet_address':wallet_address,
        'alerts':all_alerts
    }
        # Ensure we have a Redis connection (resolve lazily)
        if self.redis_con is None:
            # get_redis_connection returns a Redis instance
            try:
                self.redis_con = get_redis_connection()
            except Exception as e:
                logger.error(f"Failed to create redis connection: {e}")
                raise

        try:
            loop = asyncio.get_running_loop()
            future = asyncio.run_coroutine_threadsafe(
                self.redis_con.hset(self.user_alerts, wallet_address, json.dumps(alert_data)),
                loop
            )
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # store in Redis with address as key reference
            loop.run_until_complete(
                self.redis_con.hset(self.user_alerts, wallet_address, json.dumps(alert_data))
            )
    
    
    async def retrieve_alert(self,wallet_address:str=None):
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)

        if self.redis_con is None:
            try:
                self.redis_con = get_redis_connection()
            except Exception as e:
                logger.error(f"Failed to create redis connection: {e}")
                raise
        stored_alert = await self.redis_con.hget(self.user_alerts, wallet_address)
       
        if stored_alert is None:
            return {}

        return json.loads(stored_alert)

