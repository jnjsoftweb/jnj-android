"""
FastAPI Test Server for Rise of Kingdoms Automation

This server provides REST API endpoints to control the game automation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.adb_simple import SimpleADBController
from utils.game_controller import GameController
from utils.ui_config import reload_ui_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Rise of Kingdoms Automation API",
    description="REST API for Rise of Kingdoms game automation",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global controllers
adb_controller = None
game_controller = None


# Pydantic models
class GameStartRequest(BaseModel):
    wait_for_ready: bool = True
    auto_tap: bool = True
    force_restart: bool = False


class GameEndRequest(BaseModel):
    force: bool = False


class ScreenshotRequest(BaseModel):
    save_path: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize controllers on startup"""
    global adb_controller, game_controller

    logger.info("Starting ROK Automation API Server...")

    try:
        # Initialize ADB controller
        adb_controller = SimpleADBController()
        # Try to connect, but don't fail if Waydroid is not running yet
        # It will be started automatically when needed
        try:
            if adb_controller.connect():
                logger.info("Connected to Waydroid")
            else:
                logger.warning("Waydroid not running - will start automatically when needed")
        except Exception as e:
            logger.warning(f"Could not connect to Waydroid at startup: {e}")
            logger.info("Waydroid will be started automatically when needed")

        # Initialize game controller
        game_controller = GameController(adb_controller)
        logger.info("Game controller initialized")

    except Exception as e:
        logger.error(f"Error during startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global adb_controller

    logger.info("Shutting down API server...")

    if adb_controller:
        adb_controller.disconnect()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Rise of Kingdoms Automation API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    is_connected = adb_controller.is_connected() if adb_controller else False

    return {
        "status": "healthy" if is_connected else "unhealthy",
        "adb_connected": is_connected
    }


# Game control endpoints
@app.post("/api/game/start")
async def start_game(request: GameStartRequest):
    """Start Rise of Kingdoms"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        success = game_controller.start_game(
            wait_for_ready=request.wait_for_ready,
            auto_tap=request.auto_tap,
            force_restart=request.force_restart
        )

        if success:
            return {"status": "success", "message": "Game started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start game")

    except Exception as e:
        logger.error(f"Error starting game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/stop")
async def stop_game(request: GameEndRequest):
    """Stop Rise of Kingdoms (send to background with HOME button)"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        success = game_controller.end_game(force=request.force)

        if success:
            return {"status": "success", "message": "Game stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop game")

    except Exception as e:
        logger.error(f"Error stopping game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/end")
async def end_game():
    """Completely terminate Rise of Kingdoms process (force stop)"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        success = game_controller.end_game(force=True)

        if success:
            return {"status": "success", "message": "Game terminated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to terminate game")

    except Exception as e:
        logger.error(f"Error terminating game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/restart")
async def restart_game():
    """Restart Rise of Kingdoms"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        success = game_controller.restart_game()

        if success:
            return {"status": "success", "message": "Game restarted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to restart game")

    except Exception as e:
        logger.error(f"Error restarting game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/game/status")
async def get_game_status():
    """Get current game status"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        status = game_controller.get_game_status()
        return {"status": "success", "data": status}

    except Exception as e:
        logger.error(f"Error getting game status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/game/check-main-screen")
async def check_main_screen():
    """Check if game is in main screen (fully loaded)"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        is_in_main = game_controller.is_in_main_game()
        return {
            "status": "success",
            "in_main_game": is_in_main,
            "message": "In main game screen" if is_in_main else "Not in main game (loading or at startup screen)"
        }

    except Exception as e:
        logger.error(f"Error checking main screen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/reload")
async def reload_config():
    """Reload UI configuration from JSON files"""
    try:
        reload_ui_config()
        return {
            "status": "success",
            "message": "UI configuration reloaded successfully"
        }

    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weston/check-lock")
async def check_weston_lock():
    """Check if Weston desktop is locked"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        is_locked = game_controller.is_weston_locked()
        return {
            "status": "success",
            "is_locked": is_locked,
            "message": "Weston is locked (green unlock circle detected)" if is_locked else "Weston is unlocked"
        }

    except Exception as e:
        logger.error(f"Error checking Weston lock: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weston/pixel-color")
async def get_pixel_color(x: int, y: int):
    """Get RGB color at specific coordinates"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        color = game_controller.get_pixel_color(x, y)
        if color:
            return {
                "status": "success",
                "x": x,
                "y": y,
                "color": {"r": color[0], "g": color[1], "b": color[2]},
                "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to get pixel color")

    except Exception as e:
        logger.error(f"Error getting pixel color: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/screenshot")
async def take_screenshot(request: ScreenshotRequest):
    """Take a screenshot"""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game controller not initialized")

    try:
        image = game_controller.take_screenshot(save_path=request.save_path)

        if image:
            return {
                "status": "success",
                "message": "Screenshot captured",
                "saved_to": request.save_path if request.save_path else None,
                "size": image.size
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to capture screenshot")

    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ADB control endpoints
@app.post("/api/adb/tap")
async def adb_tap(x: int, y: int):
    """Tap at coordinates"""
    if not adb_controller:
        raise HTTPException(status_code=500, detail="ADB controller not initialized")

    try:
        success = adb_controller.tap(x, y)

        if success:
            return {"status": "success", "message": f"Tapped at ({x}, {y})"}
        else:
            raise HTTPException(status_code=500, detail="Failed to tap")

    except Exception as e:
        logger.error(f"Error tapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adb/swipe")
async def adb_swipe(x1: int, y1: int, x2: int, y2: int, duration: int = 300):
    """Swipe from one point to another"""
    if not adb_controller:
        raise HTTPException(status_code=500, detail="ADB controller not initialized")

    try:
        success = adb_controller.swipe(x1, y1, x2, y2, duration)

        if success:
            return {"status": "success", "message": f"Swiped from ({x1}, {y1}) to ({x2}, {y2})"}
        else:
            raise HTTPException(status_code=500, detail="Failed to swipe")

    except Exception as e:
        logger.error(f"Error swiping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/adb/device-info")
async def get_device_info():
    """Get device information"""
    if not adb_controller:
        raise HTTPException(status_code=500, detail="ADB controller not initialized")

    try:
        info = adb_controller.get_device_info()
        return {"status": "success", "data": info}

    except Exception as e:
        logger.error(f"Error getting device info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )