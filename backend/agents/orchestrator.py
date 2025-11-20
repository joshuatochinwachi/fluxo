"""Alert Orchestrator

Listens for smart-money / whale movement events and coordinates multiple agents to
produce a consolidated alert: market confirmation, social signals, manipulation check,
portfolio relevance, AI summary, and dispatch to automation/x402 channels.

This is a prototype orchestration implementation intended to be run from a Celery
task (see `tasks/alert_tasks.process_smart_money`) or as a background consumer.
"""
from __future__ import annotations
import json
import logging
import asyncio
from typing import Dict, Any

from dataclasses import asdict

from services.external_service import ExternalService
from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames
from agents.social_agent import SocialAgent
from agents.risk_agent import RiskAgent
from agents.portfolio_agent import portfolio_agent
from services.whale_tracker import WhaleTracker, DataSource
from services.ai_insights_engine import AIInsightsEngine
from services.llm_providers import LLMClient

logger = logging.getLogger(__name__)


class AlertOrchestrator:
	def __init__(self):
		self.redis = REDIS_CONNECT
		self.social = SocialAgent(use_mock=False)
		self.risk = RiskAgent()
		self.portfolio = portfolio_agent()
		self.whale = WhaleTracker(primary_source=DataSource.MOCK)
		self.ai = AIInsightsEngine()
		self.llm = LLMClient()
		self.request_service = ExternalService()
		

	async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Process a single smart-money / whale movement event.

		Returns a consolidated payload describing findings and actions taken.
		"""
		if isinstance(event, str):
			try:
				event = json.loads(event)
			except Exception:
				logger.error("Event payload is not valid JSON")
				return {"error": "invalid_event"}

		token = event.get("token") or event.get("token_address") 
		symbol = event.get("symbol") 
		amount_usd = float(event.get("amount_usd"))
		tx = event.get("transaction_hash") 
		from_addr = event.get("from_address")
		to_addr = event.get("to_address")

		logger.info(f"Orchestrator: processing event for {symbol} ${amount_usd:,.0f}")

		# Early filter: only process large movements (>= $2M) for this workflow
		if amount_usd < 2_000_000:
			logger.info("Movement below orchestration threshold; skipping")
			return {"skipped": True, "reason": "amount_below_threshold"}

		result: Dict[str, Any] = {
			"symbol": symbol,
			"amount_usd": amount_usd,
			"tx": tx,
			"from": from_addr,
			"to": to_addr,
			"checks": {},
		}

		# 1) Market Agent: quick price-change confirmation (prototype)
		try:
			
			price_info = await self.request_service.dex_screener_price_data(token)
			if price_info:
				price_change_percent = price_info.get('price_change_1hr')
				price = price_info.get('price')
				market_confirmed = True
			else:
				price_change_percent = None
				price = None
				market_confirmed = False
            
			result["checks"]["market"] = {
				"price_change_1h_percent": price_change_percent,
				"price":price,
				"market_confirmed": market_confirmed,
			}
		except Exception as e:
			logger.exception("Market check failed")
			result["checks"]["market"] = {"error": str(e)}

		# 2) Social Agent: compute mention spike and sentiment
		try:
			social_res = await self.social.analyze_sentiment(symbol)
			# Determine spike: compare recent posts to a small baseline (prototype)
			total_posts = social_res.get("total_posts_analyzed") or len(social_res.get("by_platform", {}).get("twitter", []))
			spike = 300 if total_posts and total_posts > 50 else 50
			result["checks"]["social"] = {
				"summary": social_res.get("summary"),
				"total_posts": total_posts,
				"mentions_spike_percent": spike,
			}
		except Exception as e:
			logger.exception("Social check failed")
			result["checks"]["social"] = {"error": str(e)}

		# 3) Manipulation Agent (pattern history): use whale tracker history to determine pattern risk
		try:
			recent = await self.whale.get_recent_movements("24h")
			# simple heuristic: if many prior large movements of same token -> higher manipulation risk
			same_token_movs = [m for m in recent if getattr(m, "token", "").lower() == (symbol or "").lower()]
			manipulation_risk = "low" if len(same_token_movs) < 2 else "medium"
			result["checks"]["manipulation"] = {"recent_similar_movements": len(same_token_movs), "risk": manipulation_risk}
		except Exception as e:
			logger.exception("Manipulation check failed")
			result["checks"]["manipulation"] = {"error": str(e)}

		# 4) Portfolio Agent: check relevance for  user wallet (if provided)
		try:
			
            # Retrive all tracked Wallet
			tracked_wallets = await self.redis.smembers('tracked_wallets')
			wallets_addresses = {address.decode() for address in tracked_wallets}
			wallet_to_notify = []
			wallets_addresses = ['0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64']
			if wallets_addresses:
				# Fetch the portfolio for each wallet
				portfolio_task = [self.portfolio.analyze_portfolio(address) for address in wallets_addresses]
				portfolio_datas = await asyncio.gather(*portfolio_task)

				if portfolio_datas:
					for portfolio in portfolio_datas:
						wallet_holdings = [asdict(portf) for  portf in portfolio]
						holding_symbols = { (a.get("symbol") or a.get("token_symbol") or "").lower() for a in wallet_holdings}
						relevance = "high" if (symbol or "").lower() in holding_symbols else "low"
						if relevance == 'high':
							wallet_to_notify.append(wallet_holdings[0].get('user_address'))

				result['wallet_to_notify'] = wallet_to_notify
			
		except Exception as e:
			logger.exception("Portfolio check failed")
			result["checks"]["portfolio"] = {"error": str(e)}

		# 5) AI Analyst: generate a short natural-language summary
		try:
			# Build a short prompt summarizing the checks
			prompt = (
				f"Market: price_change={result['checks']['market'].get('price_change_1h_percent')}% ; "
				f"Social: spike={result['checks']['social'].get('mentions_spike_percent')}% ; "
				f"Manipulation risk={result['checks']['manipulation'].get('risk')} ; \n"
				f"Write a one-sentence analyst summary describing the situation for token {symbol}.")

			# Use LLM 
			for attempt in range(0,4):
				llm_resp = self.llm.Call_gemini(prompt)
				if llm_resp:
					break
				await asyncio.sleep(5) # Soometime the LLM is ovevrloaded - cooldown

			text = None
			if isinstance(llm_resp, str):
				text = llm_resp
				
			if not text:
				# Fallback structured summary
				text = (
					f"Smart wallets accumulating {symbol}. Price +{result['checks']['market'].get('price_change_1h_percent')}%, "
					f"high social traction, {result['checks']['manipulation'].get('risk')} manipulation risk."
				)
			result["ai_summary"] = text
		except Exception as e:
			logger.exception("AI summary failed")
			result["ai_summary"] = f"fallback: Smart wallets accumulating {symbol}."

		# 6) Dispatch: publish to automation and x402 channels for downstream delivery
		try:
			alert_payload = {
				"title": f"On-chain alert: large {symbol} movement",
				"summary": result.get("ai_summary"),
				"details": result,
			}
			
			# publish to automation channel (AutomationAgent will handle delivery)
			await self.redis.publish(ChannelNames.AUTOMATION.value, json.dumps(alert_payload))
			# publish to x402 channel for pro users
			await self.redis.publish(ChannelNames.X402.value, json.dumps(alert_payload))
			result["dispatched"] = True
		except Exception as e:
			logger.exception("Dispatch failed")
			result["dispatched"] = False
			result["dispatch_error"] = str(e)

		return result



