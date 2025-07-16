import uvicorn
from dotenv import load_dotenv
from pathlib import Path

if __name__ == "__main__":
    # Load environment variables
    root_dir = Path(__file__).parent.parent
    load_dotenv(root_dir / ".env")
    
    # Run the FastAPI application
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
