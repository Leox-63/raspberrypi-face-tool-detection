#!/usr/bin/env python3
"""
Enhanced LwM2M Client for Face and Tool Detection Integration
"""

import asyncio
import json
import logging
import csv
from datetime import datetime
from pathlib import Path
from lwm2m_client.client import LwM2MClient
from lwm2m_client.config import ClientConfig

class DetectionMonitor:
    """Monitor detection CSV file and update LwM2M client."""
    
    def __init__(self, client, csv_path="../detecciones.csv"):
        self.client = client
        self.csv_path = Path(csv_path)
        self.last_position = 0
        self.logger = logging.getLogger(__name__)
        
    async def start_monitoring(self):
        """Start monitoring the CSV file."""
        self.logger.info(f"Starting CSV monitoring: {self.csv_path}")
        
        while True:
            try:
                if self.csv_path.exists():
                    await self._check_new_entries()
                await asyncio.sleep(2)
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
                
    async def _check_new_entries(self):
        """Check for new CSV entries."""
        try:
            with open(self.csv_path, 'r') as f:
                lines = f.readlines()
                
            new_lines = lines[self.last_position:]
            
            for line in new_lines:
                if line.strip() and not line.startswith('timestamp'):
                    await self._process_detection(line.strip())
                    
            self.last_position = len(lines)
            
        except Exception as e:
            self.logger.error(f"CSV processing error: {e}")
            
    async def _process_detection(self, line):
        """Process detection line."""
        try:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3:
                timestamp = parts[0]
                face_detected = parts[1].lower() == 'true'
                tool_detected = parts[2]
                
                self.logger.info(f"Detection: Face={face_detected}, Tool={tool_detected}")
                
        except Exception as e:
            self.logger.error(f"Line processing error: {e}")

async def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        config = ClientConfig.from_file('config.json')
        client = LwM2MClient(config)
        monitor = DetectionMonitor(client)
        
        logger.info("Starting Enhanced LwM2M Client...")
        
        # Start monitoring task
        monitor_task = asyncio.create_task(monitor.start_monitoring())
        
        # Start client
        await client.connect()
        logger.info("Client connected")
        
        # Keep running
        await monitor_task
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
