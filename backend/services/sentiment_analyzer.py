"""
Sentiment Analysis Service
Analyzes sentiment from social media data
"""
import ast
from typing import List, Dict
import re
from collections import Counter
from services.llm_providers import LLMClient


class SentimentAnalyzer:
    """Analyze sentiment from social media posts"""
    
    def __init__(self):
        # Positive and negative keywords
        self.llm_client = LLMClient()
        self.positive_keywords = {
            'bullish', 'moon', 'buy', 'long', 'pump', 'gains', 'profit',
            'green', 'up', 'growth', 'strong', 'solid', 'good', 'great',
            'excellent', 'amazing', 'fantastic', 'love', 'best', '🚀', '📈',
            '💎', '🔥', '✅', '💪', 'gem', 'potential', 'promising'
        }
        
        self.negative_keywords = {
            'bearish', 'dump', 'sell', 'short', 'crash', 'loss', 'red',
            'down', 'weak', 'bad', 'terrible', 'awful', 'worst', 'hate',
            'scam', 'rug', '📉', '⚠', '❌', '💩', 'avoid', 'warning',
            'risky', 'danger', 'failing', 'dead'
        }
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis result
        """
        text_lower = text.lower()
        

        """
        This text is text gotten from social media posts , As a professional sentiment analyst,
        analyze the sentiment of the text based of the on postive  and negative toward the area discussed in the text.
        provide a score between -1 to 1 where -1 is very negative and 1 is very positive.
        Also provide the classification of the sentiment as positive, negative or neutral. 
        """
        # Count positive and negative keywords
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        # Calculate sentiment score (-1 to 1)
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total
        
        # Classify sentiment
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "score": score,
            "sentiment": sentiment,
            "positive_signals": positive_count,
            "negative_signals": negative_count
        }
    
    def AI_analyse_text(self, tweets: str) -> Dict:
        """
        Analyze the batch of tweets using AI model
        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis result
        """

        prompt = f"""
        You are a professional sentiment analyst.

        You will receive multiple tweets combined as a single text.  
        Your job is to analyze BOTH:
        1. The overall sentiment of the combined tweets.
        2. The sentiment distribution (how many tweets sound positive, negative, neutral).
        
        The Tweets: {tweets}

        Instructions:
        1. Read and understand the entire text.
        2. Break the text into individual tweets when possible (split by newlines or separators).
        3. Analyze each tweet separately to classify it as positive, negative, or neutral.
        4. Count how many tweets fall into each category.
        5. Determine the overall sentiment toward the topic discussed.
        6. Assign an overall sentiment score between -1 and 1:
        - -1 means very negative  
        - 0 means neutral  
        - 1 means very positive
        7. Classify the overall sentiment as: "positive", "neutral", or "negative".
        8. Provide a short explanation.

        Return ONLY the following JSON (strict format):

        {{
        "sentiment_score": <float>,
        "classification": "<positive | neutral | negative>",
        "explanation": "<short explanation>",
        "sentiment_distribution": {{
            "positive": <int>,
            "neutral": <int>,
            "negative": <int>
        }}
        }}
        """
        response = self.llm_client.Call_gemini(prompt=prompt, model="gemini-2.5-flash")
        return response
    
    def analyze_batch(self, posts: List[Dict]) -> Dict:
        """
        Analyze sentiment across multiple posts
        
        Args:
            posts: List of social media posts
            
        Returns:
            Aggregated sentiment analysis
        """
        if not posts:
            return {
                "overall_score": 0.0,
                "overall_sentiment": "neutral",
                "total_posts": 0,
                "sentiment_distribution": {
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0
                }
            }
        
        sentiments = []
        sentiment_counts = Counter()

        tweets = ""
        tweet_count = 0

        for post in posts:
            text = post.get("text", "") or post.get("title", "")
            
            if text:
                tweet_count += 1
                tweets += f"Tweet {tweet_count}:\n{text}\n\n"
        try:
            analysis_result = self.AI_analyse_text(tweets)
            analysis_result = ast.literal_eval(analysis_result)
            overall_score = analysis_result.get("sentiment_score", 0.0)
            overall_sentiment = analysis_result.get("classification", "neutral")
            sentiment_counts = analysis_result.get("sentiment_distribution", {})
        except Exception as e:
            print(f"Error parsing AI analysis result. Using Default: {e}")
            for post in posts:
                text = post.get("text", "") or post.get("title", "")
                if text:
                    result = self.analyze_text(text)
                    sentiments.append(result["score"])
                    sentiment_counts[result["sentiment"]] += 1
            
            # Calculate overall metrics
            overall_score = sum(sentiments) / len(sentiments) if sentiments else 0.0
            
            if overall_score > 0.2:
                overall_sentiment = "positive"
            elif overall_score < -0.2:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
        
        return {
            "overall_score": round(overall_score, 3),
            "overall_sentiment": overall_sentiment,
            "total_posts": len(posts),
            "sentiment_distribution": {
                "positive": sentiment_counts.get("positive", 0),
                "neutral": sentiment_counts.get("neutral", 0),
                "negative": sentiment_counts.get("negative", 0)
            },
            "positive_percentage": round(sentiment_counts.get("positive", 0) / len(posts) * 100, 1),
            "neutral_percentage": round(sentiment_counts.get("neutral", 0) / len(posts) * 100, 1),
            "negative_percentage": round(sentiment_counts.get("negative", 0) / len(posts) * 100, 1)
        }
    

    def analyze_by_platform(self, all_data: Dict[str, List[Dict]]) -> Dict:
        """
        Analyze sentiment for each platform separately
        
        Args:
            all_data: Dictionary with data from each platform
            
        Returns:
            Platform-specific sentiment analysis
        """
        results = {}
        
        for platform, posts in all_data.items():
            results[platform] = self.analyze_batch(posts)
        
        # Calculate weighted overall sentiment
        total_posts = sum(r["total_posts"] for r in results.values())
        if total_posts > 0:
            weighted_score = sum(
                r["overall_score"] * r["total_posts"]
                for r in results.values()
            ) / total_posts
        else:
            weighted_score = 0.0
        
        if weighted_score > 0.2:
            overall_sentiment = "positive"
        elif weighted_score < -0.2:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return {
            "by_platform": results,
            "overall_score": round(weighted_score, 3),
            "overall_sentiment": overall_sentiment,
            "total_posts_analyzed": total_posts
        }
