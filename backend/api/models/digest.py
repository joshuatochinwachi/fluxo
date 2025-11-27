"""Daily digest models for Fluxo

Focused on major news structure and updates (news-driven daily digest).
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class NewsSource(BaseModel):
    name: str
    url: Optional[str]
    fetched_at: str


class NewsItem(BaseModel):
    id: Optional[str]
    title: str
    summary: Optional[str]
    url: Optional[str]
    source: str
    published_at: str
    relevance: Optional[float] = Field(None, description="0-1 relevance score")
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class NewsSummary(BaseModel):
    headline: str
    subhead: Optional[str]
    top_news: List[NewsItem] = Field(default_factory=list)
    total_news_items: int = 0


class SocialSummary(BaseModel):
    overall_sentiment: Optional[float] = Field(None, description="-1..1 sentiment score")
    top_narratives: List[Dict[str, Any]] = Field(default_factory=list)
    mentions_volume: Optional[int]


class AlertsSummary(BaseModel):
    total_alerts: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)


class DigestMeta(BaseModel):
    generated_at: str
    date_range: Optional[str] = None
    sources: List[NewsSource] = Field(default_factory=list)


class DailyDigest(BaseModel):
    """Top-level daily digest structure for front-end consumption.

    This model is intentionally news-focused (no macro data for now).
    """
    digest_id: Optional[str]
    headline: str
    overall_sentiment: Optional[float] = None
    overall_flag: Optional[str] = None
    news: NewsSummary
    social: Optional[SocialSummary]=None
    alerts: Optional[AlertsSummary]=None
    recommendations: List[str] = Field(default_factory=list)
    meta: DigestMeta
    raw_payloads: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
