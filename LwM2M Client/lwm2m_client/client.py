"""
LwM2M Client Implementation
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import aiocoap
from aiocoap import resource, Context, Message, Code

from .config import ClientConfig
from .objects import DeviceObject, SecurityObject, TemperatureObject, HumidityObject, LocationObject, ConnectivityMonitoringObject


class LwM2MClient:
    """Main LwM2M Client class."""
    
    def __init__(self, config: ClientConfig):
        """Initialize the LwM2M client."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_connected = False
        self.is_running = False
        self.context: Optional[Context] = None
        self.objects: Dict[int, Any] = {}
        
        # Initialize LwM2M objects
        self._init_objects()
    
    def _init_objects(self):
        """Initialize standard LwM2M objects."""
        # Clear any existing objects to prevent duplication
        self.objects.clear()
        
        # Object 0: Security Object
        self.objects[0] = SecurityObject(self.config)
        
        # Object 3: Device Object
        self.objects[3] = DeviceObject()
        
        # Object 4: Connectivity Monitoring Object
        self.objects[4] = ConnectivityMonitoringObject()
        
        # Object 6: Location Object  
        self.objects[6] = LocationObject()
        
        # Object 3303: Temperature Sensor Object (IPSO) - SINGLE INSTANCE
        self.objects[3303] = TemperatureObject()
        
        # Object 3304: Humidity Sensor Object (IPSO) - SINGLE INSTANCE  
        self.objects[3304] = HumidityObject()
        
        # Verify each object has exactly one instance (instance 0)
        for obj_id, obj in self.objects.items():
            if 0 not in obj.instances:
                self.logger.error(f"Object {obj_id} missing instance 0!")
            elif len(obj.instances) > 1:
                self.logger.warning(f"Object {obj_id} has {len(obj.instances)} instances - should be 1")
                # Keep only instance 0
                instance_0 = obj.instances[0]
                obj.instances.clear()
                obj.instances[0] = instance_0
        
        self.logger.info(f"Initialized {len(self.objects)} LwM2M objects: {list(self.objects.keys())}")
        self.logger.info("Each object has exactly 1 instance (instance 0)")
        
        # Verify IPSO objects specifically
        if 3303 in self.objects:
            temp_obj = self.objects[3303]
            self.logger.info(f"Temperature Object: {len(temp_obj.instances)} instances, "
                           f"{len(temp_obj.instances[0])} resources")
        
        if 3304 in self.objects:
            hum_obj = self.objects[3304]
            self.logger.info(f"Humidity Object: {len(hum_obj.instances)} instances, "
                           f"{len(hum_obj.instances[0])} resources")
    
    async def connect(self):
        """Connect to the LwM2M server."""
        self.logger.info(f"Connecting to {self.config.server_uri}")
        
        try:
            # Create CoAP server context that can both send and receive requests
            # This allows us to handle incoming READ requests from Leshan
            site = resource.Site()  # Create empty site initially
            self.context = await Context.create_server_context(site, bind=('0.0.0.0', 0))
            
            # Setup CoAP resources for handling server requests
            await self._setup_coap_resources()
            
            # Perform LwM2M registration
            await self._register()
            
            self.is_connected = True
            self.logger.info("Successfully connected to LwM2M server")
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            raise
    
    async def _register(self):
        """Perform LwM2M registration with server."""
        # Try to cleanup any existing registration for this endpoint first
        await self._cleanup_existing_registration()
        
        # Build registration payload (Link Format)
        payload = self._build_registration_payload()
        
        # Create registration request with full URI
        request = Message(
            code=Code.POST,
            uri=f"{self.config.server_uri}/rd",
            payload=payload.encode('utf-8')
        )
        
        # Add query parameters for LwM2M registration
        query_params = [
            f"ep={self.config.endpoint_name}",
            f"lt={self.config.lifetime}",
            f"b={self.config.binding_mode}",
            "lwm2m=1.0"  # LwM2M protocol version
        ]
        request.opt.uri_query = query_params
        
        # Set content format for Link Format (application/link-format)
        request.opt.content_format = 40
        
        self.logger.info(f"🚀 Registering endpoint '{self.config.endpoint_name}' with server...")
        self.logger.info(f"📍 Registration URL: {self.config.server_uri}/rd")
        self.logger.info(f"🔗 Query params: {query_params}")
        
        # Send registration request
        response = await self.context.request(request).response
        
        if response.code.is_successful():
            self.logger.info("✅ Registration successful!")
            # Parse location from response for future updates
            location = response.opt.location_path
            if location:
                self.registration_location = '/'.join(location)
                self.logger.info(f"📋 Registration location: {self.registration_location}")
            else:
                self.logger.warning("⚠️  No registration location received")
        else:
            error_msg = response.payload.decode() if response.payload else "Unknown error"
            self.logger.error(f"❌ Registration failed: {response.code} - {error_msg}")
            raise Exception(f"Registration failed: {response.code} - {error_msg}")
    
    async def _cleanup_existing_registration(self):
        """Try to cleanup any existing registration for this endpoint."""
        try:
            self.logger.info(f"🧹 Attempting cleanup of existing registrations for {self.config.endpoint_name}")
            
            # Try to discover existing registration by querying the server
            # This is a best-effort cleanup
            discover_request = Message(
                code=Code.GET,
                uri=f"{self.config.server_uri}/rd"
            )
            
            # Set a short timeout for this cleanup attempt
            try:
                response = await asyncio.wait_for(
                    self.context.request(discover_request).response, 
                    timeout=3.0
                )
                
                if response.code.is_successful() and response.payload:
                    payload_str = response.payload.decode()
                    self.logger.debug(f"Server response during cleanup: {payload_str[:100]}...")
                    
                    # Look for our endpoint in the response
                    if self.config.endpoint_name in payload_str:
                        self.logger.info("⚠️  Found existing registration, server should handle cleanup")
                
            except asyncio.TimeoutError:
                self.logger.debug("Cleanup discovery timed out (normal)")
            except Exception as e:
                self.logger.debug(f"Cleanup discovery failed: {e} (normal)")
                
        except Exception as e:
            self.logger.debug(f"Cleanup attempt failed: {e} (continuing anyway)")
            # Continue with registration even if cleanup fails
    
    def _build_registration_payload(self) -> str:
        """Build registration payload with object links in Link Format - ULTRA MINIMAL VERSION."""
        links = []
        
        # ULTRA CRITICAL FIX: Only register object instances, NO object definitions
        # This prevents Leshan from interpreting each link as a separate object
        for obj_id, obj_instance in self.objects.items():
            # ONLY register the object instance (NOT the object definition)
            # This is the absolute minimal registration
            links.append(f"</{obj_id}/0>")
        
        # RFC 6690 Link Format - comma separated, ULTRA minimal
        payload = ','.join(links)
        
        # Enhanced logging for debugging
        self.logger.info(f"===== ULTRA MINIMAL REGISTRATION PAYLOAD =====")
        self.logger.info(f"Endpoint: {self.config.endpoint_name}")
        self.logger.info(f"Strategy: INSTANCE-ONLY registration")
        self.logger.info(f"Total Objects: {len(self.objects)}")
        self.logger.info(f"Total Links: {len(links)} (one per object instance)")
        
        # Log each registered instance
        for obj_id in sorted(self.objects.keys()):
            self.logger.info(f"  /{obj_id}/0 -> {self.objects[obj_id].name}")
        
        self.logger.info(f"Full Payload: {payload}")
        self.logger.info(f"==============================================")
        
        return payload

    async def disconnect(self):
        """Disconnect from the LwM2M server."""
        self.logger.info("Disconnecting from server")
        
        # Send deregistration if connected
        if self.is_connected and hasattr(self, 'registration_location'):
            try:
                await self._deregister()
            except Exception as e:
                self.logger.warning(f"Failed to deregister: {e}")
        
        # Close CoAP context
        if self.context:
            await self.context.shutdown()
            self.context = None
        
        self.is_connected = False
        self.is_running = False
    
    async def _deregister(self):
        """Send deregistration message to server."""
        if hasattr(self, 'registration_location'):
            request = Message(
                code=Code.DELETE,
                uri=f"{self.config.server_uri}/{self.registration_location}"
            )
            
            response = await self.context.request(request).response
            if response.code.is_successful():
                self.logger.info("Deregistration successful")
    
    async def _send_update(self):
        """Send registration update to maintain connection."""
        if hasattr(self, 'registration_location'):
            request = Message(
                code=Code.POST,
                uri=f"{self.config.server_uri}/{self.registration_location}"
            )
            
            response = await self.context.request(request).response
            if response.code.is_successful():
                self.logger.debug("Registration update successful")
    
    def _update_sensor_data(self):
        """Update dynamic sensor data for all objects."""
        for obj_id, obj_instance in self.objects.items():
            if hasattr(obj_instance, 'update_simulated_data'):
                try:
                    obj_instance.update_simulated_data()
                    # Reduced logging - only essential info
                    # self.logger.debug(f"Updated sensor data for object {obj_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to update object {obj_id}: {e}")

    async def run(self):
        """Main client loop."""
        self.is_running = True
        self.logger.info("LwM2M client running...")
        
        update_interval = self.config.lifetime // 2  # Update at half lifetime
        last_update = asyncio.get_event_loop().time()
        last_sensor_update = asyncio.get_event_loop().time()
        sensor_update_interval = 30  # Update sensor data every 30 seconds
        
        try:
            while self.is_running and self.is_connected:
                current_time = asyncio.get_event_loop().time()
                
                # Send periodic registration updates
                if current_time - last_update > update_interval:
                    await self._send_update()
                    last_update = current_time
                
                # Update sensor data periodically
                if current_time - last_sensor_update > sensor_update_interval:
                    self._update_sensor_data()
                    last_sensor_update = current_time
                
                # Handle incoming messages (CoAP server functionality)
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error in client loop: {e}")
            raise

    async def _setup_coap_resources(self):
        """Setup CoAP resources for LwM2M objects to handle server requests."""
        
        class LwM2MResource(resource.Resource):
            def __init__(self, client, obj_id, instance_id=None, resource_id=None):
                super().__init__()
                self.client = client
                self.obj_id = obj_id
                self.instance_id = instance_id
                self.resource_id = resource_id
            
            async def render_get(self, request):
                """Handle GET requests from Leshan for LwM2M resources."""
                try:
                    path = f"/{self.obj_id}"
                    if self.instance_id is not None:
                        path += f"/{self.instance_id}"
                    if self.resource_id is not None:
                        path += f"/{self.resource_id}"
                    
                    # Reduced logging - only log to debug level
                    self.client.logger.debug(f"READ request for: {path}")
                    
                    if self.obj_id not in self.client.objects:
                        self.client.logger.debug(f"Object {self.obj_id} not found")
                        return Message(code=Code.NOT_FOUND)
                    
                    obj = self.client.objects[self.obj_id]
                    
                    if self.resource_id is not None:
                        # Single resource read - clean response for IPSO objects
                        value = obj.read_resource(self.instance_id or 0, self.resource_id)
                        if value is not None:
                            # Format the value properly based on type
                            if isinstance(value, (int, float)):
                                payload = str(value).encode('utf-8')
                            elif isinstance(value, str):
                                payload = value.encode('utf-8')
                            elif isinstance(value, datetime):
                                payload = value.isoformat().encode('utf-8')
                            else:
                                payload = str(value).encode('utf-8')
                            
                            # Only debug log, not info
                            self.client.logger.debug(f"Response {path} = {value}")
                            
                            # Clean response with proper content format
                            response = Message(code=Code.CONTENT, payload=payload)
                            response.opt.content_format = 0  # text/plain
                            return response
                        else:
                            self.client.logger.debug(f"Resource {path} has no value")
                            return Message(code=Code.NOT_FOUND)
                    
                    elif self.instance_id is not None:
                        # Object instance read - return all resources
                        instance_data = obj.instances.get(self.instance_id or 0, {})
                        if instance_data:
                            # For object instance reads, return a simple summary
                            resource_count = len(instance_data)
                            payload = f"Object {self.obj_id} instance {self.instance_id} has {resource_count} resources".encode('utf-8')
                            
                            self.client.logger.info(f"✅ Responding {path} -> {resource_count} resources")
                            
                            response = Message(code=Code.CONTENT, payload=payload)
                            response.opt.content_format = 0  # text/plain
                            return response
                        else:
                            return Message(code=Code.NOT_FOUND)
                    
                    else:
                        # Object read - return object info
                        payload = f"LwM2M Object {self.obj_id} ({obj.name}) - {len(obj.instances)} instances".encode('utf-8')
                        self.client.logger.info(f"✅ Responding {path} -> Object info")
                        return Message(code=Code.CONTENT, payload=payload)
                
                except Exception as e:
                    self.client.logger.error(f"💥 Error handling GET {path}: {e}")
                    import traceback
                    traceback.print_exc()
                    return Message(code=Code.INTERNAL_SERVER_ERROR)
        
        # Create a site for the server context to handle incoming requests
        site = resource.Site()
        
        # Add resources for each object
        for obj_id in self.objects.keys():
            obj_str = str(obj_id)
            
            # Object level: /3303
            site.add_resource([obj_str], LwM2MResource(self, obj_id))
            
            # Instance level: /3303/0
            site.add_resource([obj_str, '0'], LwM2MResource(self, obj_id, 0))
            
            # Add all available resources for this object
            if 0 in self.objects[obj_id].instances:
                instance_resources = self.objects[obj_id].instances[0].keys()
                for res_id in instance_resources:
                    res_str = str(res_id)
                    # Resource level: /3303/0/5700 - THIS IS CRUCIAL for IPSO
                    site.add_resource([obj_str, '0', res_str], 
                                    LwM2MResource(self, obj_id, 0, res_id))
                    self.logger.debug(f"🔧 Added CoAP endpoint: /{obj_id}/0/{res_id}")
        
        # Bind the site to the context (our server context)
        self.context.serversite = site
        self.logger.info(f"🌐 CoAP server ready - {len(self.objects)} objects, multiple resources")
        
        # Log the available endpoints for debugging
        total_endpoints = 0
        for obj_id in self.objects.keys():
            if 0 in self.objects[obj_id].instances:
                resource_count = len(self.objects[obj_id].instances[0])
                total_endpoints += 2 + resource_count  # object + instance + resources
                self.logger.info(f"📡 Object {obj_id} ({self.objects[obj_id].name}): {resource_count} resources")
        
        self.logger.info(f"📍 Total CoAP endpoints available: {total_endpoints}")