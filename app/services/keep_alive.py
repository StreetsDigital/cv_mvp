import asyncio
import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class KeepAliveService:
    """Service to keep Render app awake by self-pinging"""
    
    def __init__(self, app_url: str, ping_interval: int = 840):  # 14 minutes
        self.app_url = app_url
        self.ping_interval = ping_interval
        self.running = False
    
    async def start_keep_alive(self):
        """Start the keep-alive ping service"""
        self.running = True
        logger.info(f"Starting keep-alive service for {self.app_url}")
        
        while self.running:
            try:
                await asyncio.sleep(self.ping_interval)
                await self._ping_self()
            except Exception as e:
                logger.error(f"Keep-alive ping failed: {e}")
    
    async def _ping_self(self):
        """Ping the health endpoint to keep the app awake"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.app_url}/health", timeout=30) as response:
                    if response.status == 200:
                        logger.info(f"Keep-alive ping successful at {datetime.now()}")
                    else:
                        logger.warning(f"Keep-alive ping returned status {response.status}")
        except Exception as e:
            logger.error(f"Keep-alive ping error: {e}")
    
    def stop(self):
        """Stop the keep-alive service"""
        self.running = False
        logger.info("Keep-alive service stopped")