"""
Social Data Fetcher Service
Fetches data from Twitter, Farcaster, and Reddit
"""
import os
import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.config import Settings

logger = logging.getLogger(__name__)


class SocialDataFetcher:
    """Fetch social media data for sentiment analysis"""
    
    def __init__(self):
        # UPDATE: Change to twitterapi.io key
        settings = Settings()
        self.twitter_api_key = settings.twitter_api_key  # Changed from TWITTER_BEARER_TOKEN
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    
    async def fetch_twitter_data(self, token_symbol: str, limit: int = 100) -> List[Dict]:
        """
        Fetch tweets about a token using twitterapi.io
        
        Args:
            token_symbol: Token symbol (e.g., "MNT", "ETH")
            limit: Max number of tweets to fetch
            
        Returns:
            List of tweet data
        """
        try:
            if not self.twitter_api_key:
                logger.warning("Twitter API key not configured, using mock data")
                return self._get_mock_twitter_data(token_symbol, limit)
            
            # Build search query
            query = f"${token_symbol} "
            
            # Add common token names
            token_names = {
                "MNT": "Mantle Network",
                "ETH": "Ethereum",
                "BTC": "Bitcoin",
                "mETH": "Mantle Staked ETH"
            }
            
            # if token_symbol in token_names:
            #     query += f' OR "{token_names[token_symbol]}"'
            
            # Exclude spam
            # query += " -bot -airdrop -giveaway"
            
            # Calculate date range (last 24 hours)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)

            # query += f"since:{start_date.strftime("%Y-%m-%d_%H:%M:%S_UTC")} untill:{end_date.strftime("%Y-%m-%d_%H:%M:%S_UTC")}"
            
            # twitterapi.io endpoint
            url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
            
            headers = {
                "X-API-KEY": self.twitter_api_key
            }
            
            params = {
                "query": query,
                "queryType":'Latest'
                # "count": min(limit, 100),  # Max 100 per request
                # "section": "top",  # Get top tweets (most engagement)
                # "start_date": start_date.strftime("%Y-%m-%d"),
                # "end_date": end_date.strftime("%Y-%m-%d")
            }
            
            logger.info(f"Fetching Twitter data for {token_symbol} (query: {query})")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tweets = self._process_twitter_response_twitterapi(data)
                        logger.info(f"✅ Fetched {len(tweets)} tweets for {token_symbol}")
                        return tweets
                        
                    elif response.status == 429:
                        logger.warning("Twitter API rate limit hit, using mock data")
                        return self._get_mock_twitter_data(token_symbol, limit)
                        
                    else:
                        error_text = await response.text()
                        logger.error(f"Twitter API error {response.status}: {error_text}")
                        return self._get_mock_twitter_data(token_symbol, limit)
                        
        except asyncio.TimeoutError:
            logger.error("Twitter API request timed out")
            return self._get_mock_twitter_data(token_symbol, limit)
        except Exception as e:
            logger.error(f"Twitter fetch failed: {str(e)}")
            return self._get_mock_twitter_data(token_symbol, limit)
    
    def _process_twitter_response_twitterapi(self, data: Dict) -> List[Dict]:
        print('Using Twitterapi.io Response Processor')
        """
        Process twitterapi.io response format
        
        Args:
            data: Response from twitterapi.io
            
        Returns:
            Normalized tweet data
        """
        tweets = []
        
        # twitterapi.io returns results in "results" key
        results = data.get("tweets", [])
        

        
        for tweet in results:
            if tweet.get('type') != 'tweet':
                continue
            # Extract user data
            user_data = tweet.get("author", {})
            
            # Normalize to your format
            tweets.append({
                "platform": "twitter",
                "text": tweet.get("text") or tweet.get("full_text", ""),
                "created_at": tweet.get("createdAt", ""),
                "author_id": user_data.get("id", ""),
                "author_name": user_data.get("userName", ""),
                "author_followers": user_data.get("followers", 0),
                "likes": tweet.get("likeCount", 0),
                "retweets": tweet.get("retweetCount", 0),
                "replies": tweet.get("replyCount", 0)
            })
        
        return tweets
    
    def _process_farcaster_response(self, data: Dict, token_symbol: str) -> List[Dict]:
        """Process Farcaster API response"""
        casts = []
        if "messages" in data:
            for message in data["messages"]:
                cast_data = message.get("data", {}).get("castAddBody", {})
                casts.append({
                    "platform": "farcaster",
                    "text": cast_data.get("text", ""),
                    "created_at": message.get("data", {}).get("timestamp", ""),
                    "author_fid": message.get("data", {}).get("fid", ""),
                    "mentions": cast_data.get("mentions", [])
                })
        return casts
    
    def _process_reddit_response(self, data: Dict) -> List[Dict]:
        """Process Reddit API response"""
        posts = []
        if "data" in data and "children" in data["data"]:
            for child in data["data"]["children"]:
                post_data = child.get("data", {})
                posts.append({
                    "platform": "reddit",
                    "title": post_data.get("title", ""),
                    "text": post_data.get("selftext", ""),
                    "subreddit": post_data.get("subreddit", ""),
                    "created_at": datetime.fromtimestamp(post_data.get("created_utc", 0)).isoformat(),
                    "author": post_data.get("author", ""),
                    "score": post_data.get("score", 0),
                    "num_comments": post_data.get("num_comments", 0),
                    "url": post_data.get("url", "")
                })
        return posts
    
    # Mock data generators (for development/testing)
    
    def _get_mock_twitter_data(self, token_symbol: str, limit: int) -> List[Dict]:
        """Generate mock Twitter data for testing"""
        now = datetime.now()
        mock_tweets = [
            {
                "platform": "twitter",
                "text": f"${token_symbol} is looking bullish! 🚀 #crypto #DeFi",
                "created_at": (now - timedelta(hours=i)).isoformat(),
                "author_id": f"user_{i}",
                "likes": 50 + i * 10,
                "retweets": 20 + i * 5,
                "replies": 10 + i * 2
            }
            for i in range(min(limit, 10))
        ]
        return mock_tweets
    
    def _get_mock_farcaster_data(self, token_symbol: str, limit: int) -> List[Dict]:
        """Generate mock Farcaster data"""
        now = datetime.now()
        mock_casts = [
            {
                "platform": "farcaster",
                "text": f"Interesting development with {token_symbol} on Mantle L2",
                "created_at": (now - timedelta(hours=i)).isoformat(),
                "author_fid": f"fid_{i}",
                "mentions": []
            }
            for i in range(min(limit, 5))
        ]
        return mock_casts
    
    def _get_mock_reddit_data(self, token_symbol: str, limit: int) -> List[Dict]:
        """Generate mock Reddit data"""
        now = datetime.now()
        mock_posts = [
            {
                "platform": "reddit",
                "title": f"Discussion: {token_symbol} fundamentals",
                "text": f"What are your thoughts on {token_symbol}? Looking solid IMO.",
                "subreddit": "CryptoCurrency",
                "created_at": (now - timedelta(hours=i)).isoformat(),
                "author": f"redditor_{i}",
                "score": 100 + i * 20,
                "num_comments": 30 + i * 5,
                "url": f"https://reddit.com/r/CryptoCurrency/comments/{i}"
            }
            for i in range(min(limit, 5))
        ]
        return mock_posts
