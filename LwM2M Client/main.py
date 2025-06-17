#!/usr/bin/env python3
"""
LwM2M Client Main Entry Point
A Python-based Lightweight Machine to Machine client
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from lwm2m_client.client import LwM2MClient
from lwm2m_client.config import ClientConfig


def setup_logging(debug: bool = True) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


class LwM2MService:
    """LwM2M Client Service with graceful shutdown."""
    
    def __init__(self):
        self.client = None
        self.running = False
        self.shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the LwM2M service."""
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Python LwM2M Client Service...")
        
        try:
            # Load configuration
            config = ClientConfig.from_file('config.json')
            
            # Create and start the LwM2M client
            self.client = LwM2MClient(config)
            
            # Connect to the LwM2M server
            await self.client.connect()
            logger.info("Client connected successfully")
            
            self.running = True
            logger.info("LwM2M Service is running (Press Ctrl+C to stop gracefully)")
            
            # Keep the client running until shutdown
            await self.client.run()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down gracefully...")
        except Exception as e:
            logger.error(f"Error running LwM2M client: {e}")
            return 1
        finally:
            await self.stop()
        
        return 0
    
    async def stop(self):
        """Stop the LwM2M service gracefully."""
        logger = logging.getLogger(__name__)
        
        if self.client and self.running:
            logger.info("Stopping LwM2M client...")
            await self.client.disconnect()
            logger.info("LwM2M client stopped cleanly")
        
        self.running = False
        self.shutdown_event.set()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger = logging.getLogger(__name__)
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        
        # Schedule the shutdown in the event loop
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(self.stop())


async def main():
    """Main entry point for the LwM2M service."""
    service = LwM2MService()
    
    # Setup signal handlers for graceful shutdown
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, service.signal_handler)
    
    # Start the service
    exit_code = await service.start()
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nService interrupted by user")
        sys.exit(0)