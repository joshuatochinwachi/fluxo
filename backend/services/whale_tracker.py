"""
Whale Tracker Service - Enhanced with Alert Triggering
"""
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DataSource(str, Enum):
    """Available whale data sources"""
    MOCK = "mock"
    DUNE = "dune"
    NANSEN = "nansen"

class WhaleMovement:
    """Represents a large wallet movement"""

    def __init__(self, tx_hash: str, from_addr: str, to_addr: str,
                 token: str, amount: float, usd_value: float,
                 source: str = "unknown"):
        self.tx_hash = tx_hash
        self.from_address = from_addr
        self.to_address = to_addr
        self.token = token
        self.amount = amount
        self.usd_value = usd_value
        self.timestamp = datetime.now()
        self.impact_score = self._calculate_impact(usd_value)
        self.data_source = source
    
    def _calculate_impact(self, usd_value: float) -> float:
        """Calculate impact score 0-10"""
        if usd_value > 10_000_000:
            return 10.0
        elif usd_value > 5_000_000:
            return 8.5
        elif usd_value > 1_000_000:
            return 7.0
        elif usd_value > 500_000:
            return 5.0
        else:
            return 3.0
    
    def to_dict(self):
        return {
            "transaction_hash": self.tx_hash,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "token": self.token,
            "amount": self.amount,
            "usd_value": self.usd_value,
            "timestamp": self.timestamp.isoformat(),
            "impact_score": self.impact_score,
            "data_source": self.data_source
        }
    
    def should_alert(self, user_threshold: float = 1000000) -> bool:
        """Check if this movement warrants an alert"""
        return self.usd_value >= user_threshold and self.impact_score >= 7.0


class WhaleTracker:
    """
    Multi-source whale movement tracker with alert integration
    """
    
    def __init__(self, 
                 primary_source: DataSource = DataSource.MOCK,
                 api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize whale tracker
        
        Args:
            primary_source: Primary data source to use
            api_keys: Dict of API keys {"dune": "key", "nansen": "key"}
        """
        self.primary_source = primary_source
        self.api_keys = api_keys or {}
        self.min_threshold_usd = 100_000  # Track movements > $100K
        
        logger.info(f"WhaleTracker initialized (source: {primary_source})")
    
    async def get_recent_movements(
        self,
        timeframe: str = "24h",
        min_value_usd: Optional[float] = None
    ) -> list:
        """Get recent whale movements"""
        if self.primary_source == DataSource.MOCK:
            return self._get_mock_movements()
        elif self.primary_source == DataSource.DUNE:
            return await self._fetch_from_dune(timeframe, min_value_usd)
        elif self.primary_source == DataSource.NANSEN:
            return await self._fetch_from_nansen(timeframe, min_value_usd)
        
        return []
    
    def _get_mock_movements(self) -> list:
        """Mock whale movements for testing"""
        logger.info("Using mock whale data")
        
        
        return [
            WhaleMovement(
                tx_hash="0xa1b2c3d4e5f6...",
                from_addr="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                to_addr="0x28C6c06298d514Db089934071355E5743bf21d60",
                token="mnt",
                amount=1500.0,
                usd_value=5_250_000,
                source="mock"
            ),
            WhaleMovement(
                tx_hash="0xb2c3d4e5f6a7...",
                from_addr="0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",
                to_addr="0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503",
                token="USDC",
                amount=10_000_000,
                usd_value=10_000_000,
                source="mock"
            ),
            WhaleMovement(
                tx_hash="0xc3d4e5f6a7b8...",
                from_addr="0x1234567890abcdef1234567890abcdef12345678",
                to_addr="0xabcdef1234567890abcdef1234567890abcdef12",
                token="MNT",
                amount=2_000_000,
                usd_value=2_000_000,
                source="mock"
            )
        ]
    
    async def _fetch_from_dune(self, timeframe: str, min_value: Optional[float]) -> List[WhaleMovement]:
        """Fetch from Dune Analytics - TODO Week 3"""
        raise NotImplementedError("Dune integration pending Week 3")
    
    async def _fetch_from_nansen(self, timeframe: str, min_value: Optional[float]) -> List[WhaleMovement]:
        """Fetch from Nansen - TODO Week 3"""
        raise NotImplementedError("Nansen integration pending Week 3")
    
    async def check_whale_alerts(self, movements:list) -> list:
        """
        Check whale movements and create alerts for significant ones
        
        Args:
            movements: List of whale movements to check
        
        Returns:
            List of Alert objects for significant movements
        """
        # Lazy import to avoid circular dependency
        from api.models.alerts import Alert, AlertType, AlertSeverity
        import uuid
        
        alerts = []
        
        for movement in movements:
            if movement.should_alert():
                # Determine severity based on impact
                if movement.impact_score >= 9:
                    severity = AlertSeverity.CRITICAL
                    emoji = "🚨"
                elif movement.impact_score >= 7:
                    severity = AlertSeverity.HIGH
                    emoji = "🐋"
                else:
                    severity = AlertSeverity.WARNING
                    emoji = "⚠"
                
                # Create alert
                alert = Alert(
                    alert_id=str(uuid.uuid4()),
                    alert_type=AlertType.WHALE_MOVEMENT,
                    severity=severity,
                    title=f"{emoji} Large {movement.token} Movement Detected",
                    message=(
                        f"Whale moved {movement.amount:,.2f} {movement.token} "
                        f"(${movement.usd_value:,.0f}). "
                        f"From {movement.from_address[:10]}... "
                        f"to {movement.to_address[:10]}... "
                        f"Impact score: {movement.impact_score}/10"
                    ),
                    wallet_address=None,  # Global alert, not user-specific
                    current_value=movement.usd_value,
                    threshold=1000000,
                    details={
                        "tx_hash": movement.tx_hash,
                        "token": movement.token,
                        "amount": movement.amount,
                        "from": movement.from_address,
                        "to": movement.to_address,
                        "impact_score": movement.impact_score
                    },
                    triggered_by="whale_tracker"
                )
                
                alerts.append(alert)
                logger.info(f"Created whale alert: ${movement.usd_value:,.0f} {movement.token}")
        
        return alerts
    
    def get_summary(self, movements: List[WhaleMovement]) -> dict:
        """Generate summary with alert count"""
        if not movements:
            return {
                "total_movements": 0,
                "total_volume_usd": 0,
                "summary": "No whale movements detected"
            }
        
        total_volume = sum(m.usd_value for m in movements)
        high_impact = [m for m in movements if m.impact_score >= 7.0]
        alertable = [m for m in movements if m.should_alert()]
        
        by_source = {}
        for m in movements:
            by_source[m.data_source] = by_source.get(m.data_source, 0) + 1
        
        return {
            "total_movements": len(movements),
            "total_volume_usd": total_volume,
            "high_impact_movements": len(high_impact),
            "alertable_movements": len(alertable),
            "sources_used": by_source,
            "primary_source": self.primary_source.value,
            "summary": (
                f"{len(movements)} whale movements from {self.primary_source.value}. "
                f"Total volume: ${total_volume:,.0f}. "
                f"{len(alertable)} movements warrant alerts."
            )
        }
