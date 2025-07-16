from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from functools import lru_cache

from .database import get_db
from .schemas import (
    TopProductsResponse,
    ChannelActivityResponse,
    MessageSearchResponse,
    MessageSearchRequest
)
from .crud import (
    get_top_products,
    get_channel_activity,
    search_messages
)

app = FastAPI(
    title="Telegram Analytics API",
    version="1.0.0",
    description="API for analyzing medical product mentions in Telegram channels",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", status_code=200)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/reports/top-products", response_model=List[TopProductsResponse])
@lru_cache(maxsize=128)
async def get_top_products_endpoint(
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    """Get top products based on mention frequency
    
    Args:
        limit: Number of products to return (1-100)
    """
    try:
        results = get_top_products(db, limit)
        return results
    except Exception as e:
        logger.error(f"Error fetching top products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/channels/{channel_name}/activity", response_model=ChannelActivityResponse)
async def get_channel_activity_endpoint(
    channel_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db=Depends(get_db)
):
    """Get posting activity for a specific channel
    
    Args:
        channel_name: Name of the channel to analyze
        start_date: Start date for activity analysis
        end_date: End date for activity analysis
    """
    try:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
            
        result = get_channel_activity(db, channel_name, start_date, end_date)
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Channel {channel_name} not found or no activity in specified period"
            )
        return result
    except Exception as e:
        logger.error(f"Error fetching channel activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/messages", response_model=List[MessageSearchResponse])
async def search_messages_endpoint(
    request: MessageSearchRequest,
    db=Depends(get_db)
):
    """Search messages containing specific keywords
    
    Args:
        query: Search term to look for
        channel: Optional channel filter
        start_date: Optional start date for search
        end_date: Optional end date for search
        limit: Maximum number of results to return
    """
    try:
        results = search_messages(
            db,
            query=request.query,
            channel=request.channel,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit
        )
        return results
    except Exception as e:
        logger.error(f"Error searching messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
