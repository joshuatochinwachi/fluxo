"""
Fluxo Social Agent - Sentiment Analysis and Narrative Tracking
Enhanced with real data fetching capabilities
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, UTC
from enum import Enum

from services.social_data_fetcher import SocialDataFetcher
from services.sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)


class SentimentLevel(str, Enum):
    """Sentiment classification"""
    VERY_BEARISH = "very_bearish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    VERY_BULLISH = "very_bullish"


class SocialAgent:
    """
    Social Sentiment Analysis Agent with Real Data Fetching
    
    Features:
    - Twitter/X data fetching
    - Farcaster data fetching
    - Reddit data fetching
    - Sentiment analysis
    - Narrative detection
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize Social Agent
        
        Args:
            use_mock: Use mock data (False = use real APIs)
        """
        self.use_mock = use_mock
        self.data_fetcher = SocialDataFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Narrative Keywords
        self.narrative_keywords = [
            "the next solana", "undervalued gem", "new meta", "paradigm shift",
            "DePIN", "restaking", "AI + DeFi",
            "mantle", "mETH", "merchant moe", "fusionx",
            "l2", "layer 2", "defi", "yield", "staking",
            "liquid staking", "tvl growth", "yield farming"
        ]
        
        logger.info(f"SocialAgent initialized (mock={use_mock})")
    
    async def analyze_sentiment(
        self, 
        token_symbol: str,
        platforms: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze sentiment for a token across social platforms
        
        Args:
            token_symbol: Token to analyze (e.g., "MNT", "ETH")
            platforms: List of platforms (default: all)
            
        Returns:
            Comprehensive sentiment analysis
        """
        try:
            logger.info(f"Analyzing sentiment for {token_symbol}")
            
            # Fetch data from all platforms
            all_data = await self.data_fetcher.fetch_all_platforms(token_symbol)
            
            # Analyze sentiment
            sentiment_results = self.sentiment_analyzer.analyze_by_platform(all_data)
            
            # Add metadata
            sentiment_results["token_symbol"] = token_symbol
            sentiment_results["timestamp"] = datetime.now(UTC).isoformat()
            sentiment_results["platforms_analyzed"] = list(all_data.keys())
            sentiment_results["use_mock_data"] = self.use_mock
            
            # Generate summary
            sentiment_results["summary"] = self._generate_summary(sentiment_results)
            
            return sentiment_results
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            raise
    
    async def get_trending_narratives(self, token_symbol: str) -> List[Dict]:
        """
        Get trending narratives about a token
        
        Args:
            token_symbol: Token symbol
            
        Returns:
            List of trending narratives
        """
        # Fetch social data
        all_data = await self.data_fetcher.fetch_all_platforms(token_symbol)
        
        # Extract narratives from posts
        narratives = []
        all_posts = []
        
        for platform, posts in all_data.items():
            all_posts.extend(posts)
        
        # Analyze for narrative keywords
        keyword_counts = {}
        for keyword in self.narrative_keywords:
            count = sum(
                1 for post in all_posts 
                if keyword.lower() in (post.get('text', '') or post.get('title', '')).lower()
            )
            if count > 0:
                keyword_counts[keyword] = count
        
        # Sort by frequency
        sorted_narratives = sorted(
            keyword_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        narratives = [
            {
                "narrative": keyword,
                "mentions": count,
                "trending_score": min(count * 10, 100)
            }
            for keyword, count in sorted_narratives
        ]
        
        return narratives
    
    async def get_platform_breakdown(self, token_symbol: str) -> Dict:
        """
        Get sentiment breakdown by platform
        
        Args:
            token_symbol: Token symbol
            
        Returns:
            Platform-specific analysis
        """
        all_data = await self.data_fetcher.fetch_all_platforms(token_symbol)
        breakdown = {}
        
        for platform, posts in all_data.items():
            if posts:
                analysis = self.sentiment_analyzer.analyze_batch(posts)
                breakdown[platform] = {
                    "posts_analyzed": len(posts),
                    "sentiment": analysis["overall_sentiment"],
                    "score": analysis["overall_score"],
                    "positive_percentage": analysis["positive_percentage"],
                    "neutral_percentage": analysis["neutral_percentage"],
                    "negative_percentage": analysis["negative_percentage"]
                }
        
        return breakdown
    
    def _generate_summary(self, sentiment_results: Dict) -> str:
        """Generate human-readable summary"""
        overall_sentiment = sentiment_results.get("overall_sentiment", "neutral")
        total_posts = sentiment_results.get("total_posts_analyzed", 0)
        score = sentiment_results.get("overall_score", 0)
        
        sentiment_desc = {
            "positive": "Positive",
            "negative": "Negative",
            "neutral": "Neutral"
        }
        
        summary = f"{sentiment_desc.get(overall_sentiment, 'Neutral')} sentiment detected across {total_posts} social media posts. "
        summary += f"Sentiment score: {score:.2f} (-1.0 to 1.0). "
        
        # Platform breakdown
        by_platform = sentiment_results.get("by_platform", {})
        platform_summaries = []
        
        for platform, data in by_platform.items():
            if data["total_posts"] > 0:
                platform_summaries.append(
                    f"{platform.capitalize()}: {data['overall_sentiment']} ({data['total_posts']} posts)"
                )
        
        if platform_summaries:
            summary += "Platform breakdown: " + ", ".join(platform_summaries) + "."
        
        return summary
    
    def _score_to_level(self, score: float) -> SentimentLevel:
        """Convert numeric score to sentiment level"""
        if score > 0.6:
            return SentimentLevel.VERY_BULLISH
        elif score > 0.2:
            return SentimentLevel.BULLISH
        elif score > -0.2:
            return SentimentLevel.NEUTRAL
        elif score > -0.6:
            return SentimentLevel.BEARISH
        else:
            return SentimentLevel.VERY_BEARISH

