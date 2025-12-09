"""
Social Sentiment Analysis Celery Task - With Alert Triggering
"""
from core import celery_app
import asyncio
from services.alert_manager import AlertManager
from agents.social_agent import SocialAgent
import uuid
from api.models.alerts import Alert, AlertSeverity


@celery_app.task(bind=True, name="social_analysis")
def social_task(self,wallet_address :str=None, token_symbol: str=None, platforms: list = None, alert_threshold: float = 0.7):
    """
    Social sentiment analysis with alert triggering
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Fetching social sentiment...', 'progress': 0}
        )
        
        print(f'Running social sentiment analysis for: {token_symbol if token_symbol else wallet_address}')
        
        
        
        # Default platforms
        if platforms is None:
            platforms = ["twitter", "farcaster", "reddit"]
        
        # Run async agent code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # self.update_state(
        #     state='PROCESSING',
        #     meta={'status': 'Analyzing sentiment across platforms...', 'progress': 30}
        # )
        
        # Execute sentiment analysis using SocialAgent
        social_agent = SocialAgent(use_mock=False)
        alert_manager = AlertManager()
        # If wallet_address provided, fetch user portfolio and analyze holdings
        holdings_to_analyze = []
        portfolio_holdings = None
        if wallet_address:
            try:
                from agents.portfolio_agent import portfolio_agent
                portfolio = portfolio_agent()
                portfolio_holdings = loop.run_until_complete(
                    portfolio.retrieve_portfolio_data(wallet_address)
                )
                if portfolio_holdings:
                    for h in portfolio_holdings:
                        # dataclass or dict
                        symbol = None
                        weight = 0.0
                        if hasattr(h, 'token_symbol'):
                            symbol = getattr(h, 'token_symbol')
                            weight = getattr(h, 'percentage_of_portfolio', 0.0)
                        elif isinstance(h, dict):
                            symbol = h.get('token_symbol')
                            weight = h.get('percentage_of_portfolio', 0.0)

                        if symbol:
                            holdings_to_analyze.append({
                                'symbol': symbol,
                                'weight': float(weight) / 100.0 if weight is not None else 0.0
                            })
            except Exception as e:
                print('Failed to fetch portfolio for wallet', wallet_address, e)

        # If no holdings found, fall back to single token_symbol
        if not holdings_to_analyze:
            if token_symbol:
                holdings_to_analyze = [{'symbol': token_symbol, 'weight': 1.0}]
            else:
                holdings_to_analyze = []

        # Analyze each symbol and aggregate weighted score
        per_token_results = []
        for entry in holdings_to_analyze:
            sym = entry['symbol']
            try:
                res = loop.run_until_complete(social_agent.analyze_sentiment(sym, platforms))
            except Exception:
                res = {'overall_score': 0.0, 'trend': 'neutral', 'volume_change': 1.0, 'platforms_analyzed': platforms or []}

            per_token_results.append({'symbol': sym, 'weight': entry.get('weight', 1.0), 'result': res})

        total_weight = sum(p['weight'] for p in per_token_results) or 1.0
        weighted_sum = sum((p['result'].get('overall_score', 0.0) or 0.0) * p['weight'] for p in per_token_results)
        over_all_score = sum(p['result'].get('overall_score', 0.0) or 0.0 for p in per_token_results)

        aggregate_score = weighted_sum / total_weight if per_token_results else 0.0

        sentiment_result = {
            'per_token': per_token_results,
            'overall_score': over_all_score,
            'aggregate_score': aggregate_score,
            'platforms_analyzed': platforms or []
        }
        
        # self.update_state(
        #     state='PROCESSING',
        #     meta={'status': 'Checking sentiment alerts...', 'progress': 70}
        # )
        
        # Trigger alerts for extreme sentiment
        triggered_alerts = []

        # Determine previous score (baseline) and compute delta
        identifier = wallet_address if wallet_address else token_symbol
        try:
            previous_score = alert_manager.get_last_sentiment(identifier)
        except Exception:
            previous_score = None

        # Use aggregate score when analyzing a portfolio
        if 'aggregate_score' in sentiment_result:
            score = sentiment_result.get('aggregate_score', 0.0)
            # compute weighted average volume_change if per_token present
            if sentiment_result.get('per_token'):
                total_w = sum(p.get('weight', 1.0) for p in sentiment_result['per_token']) or 1.0
                volume_change = sum((p['result'].get('volume_change', 1.0) or 1.0) * p.get('weight', 1.0) for p in sentiment_result['per_token']) / total_w
                sentiment_result['volume_change'] = volume_change
            else:
                volume_change = 1.0
                sentiment_result['volume_change'] = volume_change
        else:
            score = sentiment_result.get('overall_score', 0.0)
            volume_change = sentiment_result.get('volume_change', 1.0)
            sentiment_result['volume_change'] = volume_change

        delta_score = abs(score - previous_score) if previous_score is not None else 0.0

        # SENTIMENT_SHIFT rule: magnitude or rapid change + volume spike
        try:
            if (abs(score) >= 0.6 and volume_change >= 1.2) or (delta_score >= 0.3):
                if score <= -0.6 or delta_score >= 0.5:
                    severity_enum = AlertSeverity.CRITICAL
                elif score <= -0.4 or delta_score >= 0.3:
                    severity_enum = AlertSeverity.HIGH
                else:
                    severity_enum = AlertSeverity.WARNING

                alert = alert_manager._create_sentiment_shift_alert(
                    identifier, score, delta_score, volume_change, severity=severity_enum
                )
                if alert:
                    # store and append (associate with user's wallet if present)
                    store_wallet = wallet_address if wallet_address else 'global'
                    triggered_alerts.append(alert.to_dict())
        except Exception as e:
            print('Sentiment alert eval failed:', e)

        # NARRATIVE_TRENDING rule: check narratives
        try:
            # If portfolio analyzed, check narratives per token; else check for single token
            tokens_for_narratives = [p['symbol'] for p in sentiment_result.get('per_token', [])] if sentiment_result.get('per_token') else ([token_symbol] if token_symbol else [])
            for sym in tokens_for_narratives:
                narratives = loop.run_until_complete(social_agent.get_trending_narratives(sym))
                for n in narratives:
                    mentions = n.get('mentions', 0)
                    trending_score = n.get('trending_score', 0)
                    if trending_score >= 30 or mentions >= 10:
                        alert = alert_manager._create_narrative_trending_alert(
                            sym, n.get('narrative', 'unknown'), mentions, trending_score
                        )
                        if alert:
                            alert = alert.to_dict()
                            if trending_score > sentiment_result.get('trend_score', 0):
                                sentiment_result['trend'] = sym
                                sentiment_result['trend_score'] = trending_score
                                sentiment_result['message'] = alert.get('message', '')
                            store_wallet = wallet_address if wallet_address else 'global'
                            # alert_manager.store_alert([alert.to_dict()], wallet_address=store_wallet)
                            triggered_alerts.append(alert)
        except Exception as e:
            print('Narrative check failed:', e)
        loop.close()
        # update baseline sentiment (store by wallet identifier if provided)
        try:
            alert_manager.set_last_sentiment(identifier, float(score))
        except Exception:
            pass
        
        print(f"Social analysis completed: aggregate_score={sentiment_result.get('aggregate_score', sentiment_result.get('overall_score'))}")
        print(f'Triggered {len(triggered_alerts)} Social sentiment alerts')
        
        return {
            'status': 'completed',
            'token_symbol': token_symbol,
            'sentiment_analysis': sentiment_result,
            'platforms_analyzed': platforms,
            'alerts_triggered': len(triggered_alerts),
            'alerts': triggered_alerts,
            'agent': 'social',
            'version': '2.0_with_alerts'
        }
        
    except Exception as e:
        print(f'Social analysis failed: {str(e)}')
        
        # self.update_state(
        #     state='FAILURE',
        #     meta={'error': str(e)}
        # )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'social'
        }
