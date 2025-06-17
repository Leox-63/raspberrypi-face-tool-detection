"""
LwM2M Client Configuration
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ClientConfig:
    """Configuration for LwM2M client."""
    
    # Server settings
    server_uri: str = "coap://192.168.0.100:5683"
    server_host: str = "192.168.0.100"
    server_port: int = 5683
    
    # Client identification
    endpoint_name: str = "python-lwm2m-client"
    lifetime: int = 86400  # 24 hours
    binding_mode: str = "U"  # UDP binding
    
    # Security settings
    use_dtls: bool = False
    psk_identity: Optional[str] = None
    psk_key: Optional[str] = None
    
    # CoAP settings
    coap_port: int = 0  # 0 for auto-assign
    max_retransmit: int = 4
    ack_timeout: float = 2.0
    
    @classmethod
    def load_default(cls):
        """Load default configuration."""
        return cls()
    
    @classmethod
    def from_file(cls, config_path: str):
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except Exception:
            return cls.load_default()
    
    def save_to_file(self, config_path: str):
        """Save configuration to file."""
        data = {
            'server_uri': self.server_uri,
            'endpoint_name': self.endpoint_name,
            'lifetime': self.lifetime,
            'binding_mode': self.binding_mode
        }
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)