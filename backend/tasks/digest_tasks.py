"""Daily digest aggregation tasks

This task collects news from multiple sources, social summaries, and alert
counts and produces a `DailyDigest` (news-focused). The fetchers are
placeholders so you can wire real HTTP clients / pipeline outputs later.
"""
import asyncio
import json
import logging

from celery import shared_task
from core import celery_app
from services.external_service import ExternalService
from datetime import datetime, timedelta

from typing import List, Dict, Any, Optional

from api.models.digest import (
	DailyDigest, NewsSummary, NewsItem, NewsSource, SocialSummary, AlertsSummary, DigestMeta
)
from core.config import MONGO_CONNECT, get_redis_connection

logger = logging.getLogger(__name__)



# @celery_app.task(name='daily_news_digest')
@shared_task
def daily_news_digest(date: Optional[str] = None):
	"""Generate a news-focused daily digest and store it in Mongo + Redis.

	Args:
		date: optional YYYY-MM-DD string for the digest date; defaults to today UTC.
	"""
	try:
		generated_at = datetime.utcnow()
		date_range = date or generated_at.strftime('%Y-%m-%d')

		# Fetch and normalize news
		raw_news = _fetch_news_sources()
		news_items = [
			NewsItem(
				id=i.get('id'),
				title=i.get('title'),
				summary=i.get('summary'),
				url=i.get('url'),
				source=i.get('source'),
				published_at=i.get('published_at'),
				relevance=i.get('relevance'),
				categories=i.get('categories', []),
				tags=i.get('tags', [])
			).model_dump()
			for i in raw_news
		]

		news_summary = NewsSummary(
			headline=news_items[0]['title'] if news_items else 'No major news',
			subhead=None,
			top_news=[NewsItem.model_validate(n) for n in news_items][:5],
			total_news_items=len(news_items)
		)
        
		# # Social summary
		# ss = _fetch_social_summary()
		# social = SocialSummary(
		# 	overall_sentiment=ss.get('overall_sentiment'),
		# 	top_narratives=ss.get('top_narratives', []),
		# 	mentions_volume=ss.get('mentions_volume')
		# )

		# # Alerts summary
		# asu = _fetch_alerts_summary()
		# alerts = AlertsSummary(total_alerts=asu.get('total_alerts', 0), by_type=asu.get('by_type', {}))

		digest = DailyDigest(
			digest_id=None,
			headline=news_summary.headline,
			overall_sentiment=None,
			overall_flag=None,
			news=news_summary,
			social=None,
			alerts=None,
			recommendations=[],
			meta=DigestMeta(generated_at=str(generated_at.strftime('%Y-%m-%d')), date_range=date_range, sources=[NewsSource(name='DemoNews', url='https://demo.news', fetched_at=str(generated_at.strftime('%Y-%m-%d')))]),
			raw_payloads={
				'news_raw': {}
			}
		)
		# Persist to Mongo (historical) and Redis (latest)
		# print(digest.to_dict())
		# try:
		# 	db = MONGO_CONNECT
		# 	coll = db.get_collection('daily_digests')
		# 	doc = digest.model_dump()
		# 	doc['generated_at'] = generated_at
		# 	res = coll.insert_one(doc)
		# 	digest_id = str(res.inserted_id)
		# 	digest.digest_id = digest_id
		# except Exception as e:
		# 	logger.exception('Failed to write digest to Mongo: %s', e)
		# 	digest_id = None

		# Save latest digest to Redis (stringified)
		loop = asyncio.get_event_loop()
		asyncio.set_event_loop(loop)
		digest = digest.to_dict()
		try:
			redis_conn = get_redis_connection()
			redis_key = f"digest:latest:news:{date_range}"
			store = loop.run_until_complete(
				redis_conn.hset("Daily_Digest","Digest",json.dumps(digest))
            )
			print('Stored in Redis')
		except Exception as e:
			logger.exception('Failed to write latest digest to Redis: %s', e)

		# return {
		# 	'status': 'completed',
		# 	'date': date_range,
		# 	'digest_id': digest.digest_id,
		# 	'headline': digest.headline
		# }

	except Exception as e:
		logger.exception('daily_news_digest failed: %s', e)
		return {'status': 'failed', 'error': str(e)}




def _fetch_news_sources() -> List[Dict[str, Any]]:
	"""
	Placeholder: fetch news from multiple APIs and normalize to list of dicts.
	"""
	
	# TODO: replace with real fetchers (CoinGecko/news API, Flipside feeds, etc.)
	external_service = ExternalService()
	src = ""
	items = [
		{
			'id': 'n1',
			'title': 'BTC dips 5% amid volume surge',
			'summary': 'Bitcoin price fell 5% in the last 24h on heavy selling.',
			'url': 'https://demo.news/btc-dip',
			'source': src,
			'published_at': '',
			'relevance': 0.9,
			'categories': ['market', 'price'],
			'tags': ['BTC', 'market']
		},
		{
			'id': 'n2',
			'title': 'Stablecoin flows increase to exchanges',
			'summary': 'Large inflows into USDC observed on major exchanges.',
			'url': 'https://demo.news/stablecoin-flows',
			'source': src,
			'published_at':'',
			'relevance': 0.7,
			'categories': ['flows'],
			'tags': ['USDC']
		}
	]
	loop = asyncio.get_event_loop()
	asyncio.set_event_loop(loop)
	
	items = loop.run_until_complete(
		external_service.Coindesk_news()
    )
	loop.close
	return items
    

def _fetch_social_summary() -> Dict[str, Any]:
	"""Placeholder: return a simple social sentiment snapshot."""
	return {
		'overall_sentiment': 0.12,
		'top_narratives': [
			{'narrative': 'L2 adoption', 'mentions': 150, 'score': 72},
			{'narrative': 'stablecoin flows', 'mentions': 90, 'score': 60}
		],
		'mentions_volume': 500
	}


def _fetch_alerts_summary() -> Dict[str, Any]:
	"""Placeholder: count alerts from AlertManager / Redis keys."""
	return {
		'total_alerts': 2,
		'by_type': {'risk': 1, 'macro': 0, 'social': 1}
	}




