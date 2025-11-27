from .automation import router as automation_router
from .execution import router as execution_router
from .governace import router as governance_router
from .macro import router as macro_router
from .market_data import router as market_data_router
from .onchain import router as onchain_router
from .portfolio import router as portfolio_router
from .research import router as research_router
from .risk import router as risk_router
from .x402 import router as x402_router
from .yield_opportunity import router as yield_router
from .social import router as social_router
from .alerts import router as alerts_router
from .system import router as system_router
from .digest import router as digest_router


__all__ = [
    'automation_router',
    'execution_router',
    'governance_router',
    'macro_router',
    'market_data_router',
    'onchain_router',
    'portfolio_router',
    'research_router',
    'risk_router',
    'x402_router',
    'yield_router',
    'social_router',
    'alerts_router',
    'system_router',
    'digest_router'
    
]
