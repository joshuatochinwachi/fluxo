import logging
from typing import AsyncIterator,Optional

from pydantic import BaseModel
from core.config import MANTLE_WSS_URL

from web3 import AsyncWeb3,WebSocketProvider
from eth_abi import decode
from eth_abi.exceptions import InsufficientDataBytes
from eth_utils import to_checksum_address

logger = logging.getLogger(__name__)

class TranferReponse(BaseModel):
    token: str
    from_address: str
    to_address: str
    amount: int
    transaction_hash: str
    block_number: int

class TokenListener:
    def __init__(self):
        transfer_event_signature = "Transfer(address,address,uint256)"
        self.tranfer_topic = [ AsyncWeb3.keccak(text=transfer_event_signature)]
        self.subscription_id : Optional[str] = None
        self.w3 = None

    # Listen to Transfer Events
    async def tranfers_event(self) -> AsyncIterator[dict]:
        async with AsyncWeb3(WebSocketProvider(MANTLE_WSS_URL)) as w3:
            self.w3 = w3

            params = {
                "address": None,
                "topics": self.tranfer_topic
            }
            self.subscription_id = await w3.eth.subscribe("logs", params)
            print(f"Subscribed to Transfer events with subscription ID: {self.subscription_id}")

            async for payload in w3.socket.process_subscriptions():
                if payload.get("subscription") != self.subscription_id:
                        continue
                        
                log = payload.get("result")
                if not log:
                    continue
                
                # Determine event type from topic0
                topic0 = log.get("topics", [])[0] if log.get("topics") else None
                if not topic0:
                    continue

                if topic0 != self.tranfer_topic[0]:
                    continue

                transfer_event = await self.parse_transfer_event(log)
                if not transfer_event:
                    continue
                yield transfer_event

    # Pasrse Transfer Event Log
    async def parse_transfer_event(self,log:dict)->TranferReponse|None:
        try:
            topics = log.get("topics", [])
            data = log.get("data", "0x")

            from_address = to_checksum_address("0x" + topics[1].hex()[24:])
            to_address = to_checksum_address("0x" + topics[2].hex()[24:])
            
            if isinstance(data, str):
                data =  bytes.fromhex(data[2:] if data.startswith('0x') else data)
        
            amount = decode(['uint256'], data)[0]
            return TranferReponse(
                token=to_checksum_address(log.get("address")),
                from_address=from_address,
                to_address=to_address,
                amount=amount,
                transaction_hash= "0x" + log.get("transactionHash").hex(),
                block_number=log.get("blockNumber")
            )
        except InsufficientDataBytes as e:
            logger.error(f"Error decoding event data: {e}")
            return None
        
    # Unsubscribe from events
    async def unsubscribe(self):
        if self.subscription_id and self.w3:
            await self.w3.eth.unsubscribe(self.subscription_id)
