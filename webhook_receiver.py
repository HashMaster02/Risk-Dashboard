from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
from data_storage import db_manager

app = FastAPI(
    title="TradingView Webhook Receiver",
    description="Receives investment data from TradingView webhooks",
    version="1.0.0"
)

class WebhookData(BaseModel):
    """Expected webhook payload from TradingView"""
    symbol: str = Field(..., description="Stock/crypto ticker symbol")
    price: float = Field(..., description="Current closing price")
    atr: float = Field(..., description="Average True Range value")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "price": 150.25,
                "atr": 2.35
            }
        }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "TradingView Webhook Receiver",
        "endpoints": {
            "webhook": "/webhook (POST)",
            "health": "/ (GET)"
        }
    }

@app.post("/webhook")
async def receive_webhook(data: WebhookData):
    """
    Receive webhook data from TradingView

    Expected JSON format:
    {
        "symbol": "{{ticker}}",
        "price": {{close}},
        "atr": {{plot("ATR")}}
    }
    """
    try:
        # Validate data
        if data.price <= 0:
            raise HTTPException(status_code=400, detail="Price must be positive")
        if data.atr < 0:
            raise HTTPException(status_code=400, detail="ATR cannot be negative")

        # Store in database
        success = db_manager.insert_data(
            symbol=data.symbol,
            price=data.price,
            atr=data.atr
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to store data")

        return {
            "status": "success",
            "message": f"Data for {data.symbol} received and stored",
            "data": {
                "symbol": data.symbol,
                "price": data.price,
                "atr": data.atr,
                "exit_price": data.price - data.atr
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check with database status"""
    try:
        # Test database connection
        data = db_manager.get_latest_data_per_symbol()
        return {
            "status": "healthy",
            "database": "connected",
            "records_count": len(data)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "webhook_receiver:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
