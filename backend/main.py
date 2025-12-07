"""
Boing - API Abuse & Cybersecurity Monitoring Platform
Main FastAPI application entry point
"""
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from database import init_db, close_db
from routes import auth, apis, ingest, alerts, metrics, admin, profile
from detection_engine import DetectionEngine
from alert_service import AlertService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
detection_engine = None
alert_service = None
websocket_connections = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global detection_engine, alert_service
    
    # Startup
    logger.info("Starting Boing API Monitoring Platform...")
    init_db()
    
    # Initialize services
    alert_service = AlertService()
    detection_engine = DetectionEngine(alert_service)
    
    # Make services available to routes
    app.state.detection_engine = detection_engine
    app.state.alert_service = alert_service
    app.state.broadcast = broadcast_to_websockets
    
    # Start background tasks
    asyncio.create_task(detection_engine.start())
    
    logger.info("Boing is ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Boing...")
    if detection_engine:
        await detection_engine.stop()
    close_db()
    logger.info("Boing stopped.")


# Create FastAPI app
app = FastAPI(
    title="Boing API",
    description="API Abuse & Cybersecurity Monitoring Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(apis.router, prefix="/api", tags=["API Management"])
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(metrics.router, prefix="/api", tags=["Metrics"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Boing API Monitoring Platform",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "detection_engine": "running" if detection_engine else "stopped",
        "alert_service": "running" if alert_service else "stopped"
    }


@app.websocket("/ws/live")
async def websocket_live_feed(websocket: WebSocket):
    """WebSocket endpoint for live activity feed"""
    await websocket.accept()
    websocket_connections.add(websocket)
    logger.info(f"WebSocket client connected. Total: {len(websocket_connections)}")
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(websocket_connections)}")


async def broadcast_to_websockets(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    disconnected = set()
    for ws in websocket_connections:
        try:
            await ws.send_json(message)
            logger.info(f"Broadcasted message to WebSocket: {message.get('type')}")
        except Exception as e:
            logger.error(f"Error broadcasting to WebSocket: {e}")
            disconnected.add(ws)
    
    # Clean up disconnected clients
    websocket_connections.difference_update(disconnected)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
