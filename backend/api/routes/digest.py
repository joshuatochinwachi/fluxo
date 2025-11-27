import json
from core.config import get_redis_connection
from fastapi import APIRouter
from ..models.digest import NewsItem

router = APIRouter()

@router.get('/digest')
async def digest_news():
    """
    Get the daily digest from the redis db
    """
    redis_con = get_redis_connection()
    news_data = await redis_con.hget('Daily_Digest','Digest')
    if not news_data:
        return 
    
    news_data = json.loads(news_data.decode('utf-8'))
    top_news = news_data.get('news',{}).get('top_news')
    if  not top_news:
        return 
    
    return [
        NewsItem(
            id=nw.get('id',''),
            title=nw.get('title',''),
            summary=nw.get('summary',''),
            url=nw.get('url',''),
            source=nw.get('source',''),
            published_at=nw.get('published_at',''),
            relevance=nw.get('relevance',0.9),
            categories=nw.get('categories',[]),
            tags=nw.get('tags',[])
        )
        for nw in top_news
        
    ]


