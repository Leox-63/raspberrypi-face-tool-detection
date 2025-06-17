"""
LwM2M Client Package
A Python implementation of the OMA LwM2M protocol for IoT device management.
"""

__version__ = "1.0.0"
__author__ = "LwM2M Client Team"

from .client import LwM2MClient
from .config import ClientConfig

__all__ = ["LwM2MClient", "ClientConfig"]