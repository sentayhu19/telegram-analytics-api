from typing import List, Optional
from datetime import datetime, timedelta
import logging
from functools import lru_cache

from .schemas import (
    TopProductsResponse,
    ChannelActivityResponse,
    MessageSearchRequest,
    MessageSearchResponse
)

logger = logging.getLogger(__name__)

def _execute_query_with_retry(db, query: str, params: dict = None, retries: int = 3) -> List:
    """Execute query with retry mechanism"""
    for attempt in range(retries):
        try:
            cur = db.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            return cur.fetchall()
        except Exception as e:
            if attempt == retries - 1:
                raise
            logger.warning(f"Query failed, retrying ({attempt + 1}/{retries}): {str(e)}")
            continue

@lru_cache(maxsize=128)
def get_top_products(db, limit: int = 10) -> List[TopProductsResponse]:
    """Get top products based on mention frequency"""
    try:
        results = _execute_query_with_retry(db, """
            SELECT 
                ch.channel_name,
                p.product_name,
                COUNT(*) as mention_count,
                MIN(m.message_ts) as first_mention,
                MAX(m.message_ts) as last_mention,
                AVG(p.confidence_score) as avg_confidence
            FROM telegram_mart.product_mentions p
            JOIN telegram_mart.channels ch ON ch.channel_id = p.channel_id
            JOIN telegram_mart.messages m ON m.message_id = p.message_id
            GROUP BY ch.channel_name, p.product_name
            ORDER BY mention_count DESC
            FETCH FIRST :limit ROWS ONLY
        """, {"limit": limit})
        
        return [
            TopProductsResponse(
                channel=channel,
                product=ProductMention(
                    product_name=product_name,
                    mention_count=mention_count,
                    first_mention=first_mention,
                    last_mention=last_mention
                ),
                confidence_score=avg_confidence
            )
            for channel, product_name, mention_count, first_mention, last_mention, avg_confidence in results
        ]
    except Exception as e:
        logger.error(f"Error in get_top_products: {str(e)}")
        raise

@lru_cache(maxsize=64)
def get_channel_activity(
    db, 
    channel_name: str,
    start_date: datetime,
    end_date: datetime
) -> ChannelActivityResponse:
    """Get posting activity for a specific channel"""
    try:
        results = _execute_query_with_retry(db, """
            WITH daily_stats AS (
                SELECT 
                    TRUNC(m.message_ts) as date,
                    COUNT(*) as message_count,
                    AVG(LENGTH(m.message_text)) as avg_message_length,
                    COUNT(CASE WHEN m.media_type = 'image' THEN 1 END) as image_count,
                    COUNT(CASE WHEN m.media_type = 'video' THEN 1 END) as video_count
                FROM telegram_mart.messages m
                JOIN telegram_mart.channels c ON c.channel_id = m.channel_id
                WHERE c.channel_name = :channel_name
                AND m.message_ts BETWEEN :start_date AND :end_date
                GROUP BY TRUNC(m.message_ts)
            )
            SELECT 
                ds.date,
                ds.message_count,
                ds.avg_message_length,
                ds.image_count,
                ds.video_count
            FROM daily_stats ds
            ORDER BY ds.date
        """, {
            "channel_name": channel_name,
            "start_date": start_date,
            "end_date": end_date
        })
        
        if not results:
            return None
            
        activity_history = [
            ChannelActivity(
                date=date,
                message_count=message_count,
                avg_message_length=avg_message_length,
                image_count=image_count,
                video_count=video_count
            )
            for date, message_count, avg_message_length, image_count, video_count in results
        ]
        
        total_messages = sum(item.message_count for item in activity_history)
        total_media = sum(item.image_count + item.video_count for item in activity_history)
        avg_daily_messages = total_messages / len(activity_history) if activity_history else 0
        
        return ChannelActivityResponse(
            channel_name=channel_name,
            activity_history=activity_history,
            total_messages=total_messages,
            total_media=total_media,
            avg_daily_messages=avg_daily_messages
        )
    except Exception as e:
        logger.error(f"Error in get_channel_activity: {str(e)}")
        raise

def search_messages(
    db,
    query: str,
    channel: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 10
) -> List[MessageSearchResponse]:
    """Search messages containing specific keywords"""
    try:
        params = {
            "query": f"%{query}%",
            "limit": limit
        }
        
        where_clauses = []
        if channel:
            where_clauses.append("c.channel_name = :channel_name")
            params["channel_name"] = channel
        
        if start_date:
            where_clauses.append("m.message_ts >= :start_date")
            params["start_date"] = start_date
        
        if end_date:
            where_clauses.append("m.message_ts <= :end_date")
            params["end_date"] = end_date
        
        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        results = _execute_query_with_retry(db, f"""
            SELECT 
                m.message_id,
                c.channel_name,
                m.message_text as content,
                m.message_ts as timestamp,
                m.media_type,
                m.sentiment_score,
                m.confidence_score
            FROM telegram_mart.messages m
            JOIN telegram_mart.channels c ON c.channel_id = m.channel_id
            {where_clause}
            AND (LOWER(m.message_text) LIKE LOWER(:query))
            ORDER BY m.message_ts DESC
            FETCH FIRST :limit ROWS ONLY
        """, params)
        
        return [
            MessageSearchResponse(
                message_id=message_id,
                channel=channel_name,
                content=content,
                timestamp=timestamp,
                media_type=media_type,
                sentiment_score=sentiment_score,
                confidence_score=confidence_score
            )
            for message_id, channel_name, content, timestamp, media_type, sentiment_score, confidence_score in results
        ]
    except Exception as e:
        logger.error(f"Error in search_messages: {str(e)}")
        raise
