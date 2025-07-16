from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductMention(BaseModel):
    product_name: str
    mention_count: int
    first_mention: datetime
    last_mention: datetime

class TopProductsResponse(BaseModel):
    channel: str
    product: ProductMention
    confidence_score: float

class ChannelActivity(BaseModel):
    date: datetime
    message_count: int
    avg_message_length: float
    image_count: int
    video_count: int

class ChannelActivityResponse(BaseModel):
    channel_name: str
    activity_history: List[ChannelActivity]
    total_messages: int
    total_media: int
    avg_daily_messages: float

class MessageSearchRequest(BaseModel):
    query: str
    channel: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 10

class MessageSearchResponse(BaseModel):
    message_id: int
    channel: str
    content: str
    timestamp: datetime
    media_type: Optional[str] = None
    sentiment_score: Optional[float] = None
    confidence_score: Optional[float] = None
