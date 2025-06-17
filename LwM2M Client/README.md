# Python LwM2M Client

A Python implementation of the OMA Lightweight Machine to Machine (LwM2M) protocol client, designed to replace Java Leshan implementations.

## Features

- **Pure Python Implementation**: No Java dependencies required
- **Async/Await Support**: Built with modern Python async programming
- **Standard LwM2M Objects**: Implements Security, Device, and Server objects
- **CoAP Protocol**: Uses aiocoap for efficient CoAP communication
- **Configurable**: JSON-based configuration system
- **Extensible**: Easy to add custom LwM2M objects

## Installation

1. Clone or download this project
2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.json` to configure your LwM2M server connection:

```json
{
  "server_uri": "coap://localhost:5683",
  "endpoint_name": "python-lwm2m-client",
  "lifetime": 86400
}
```

## Usage

Run the LwM2M client:

```bash
python main.py
```

## Project Structure

- `main.py` - Main entry point
- `lwm2m_client/` - Core client package
  - `client.py` - Main LwM2M client implementation
  - `config.py` - Configuration management
  - `objects.py` - Standard LwM2M objects
- `config.json` - Client configuration
- `requirements.txt` - Python dependencies

## Development

This project uses:
- Python 3.8+
- aiocoap for CoAP protocol
- asyncio for asynchronous operations

## TODO

- [ ] Complete CoAP message handling
- [ ] Implement observation mechanism
- [ ] Add more standard LwM2M objects
- [ ] Implement DTLS security
- [ ] Add unit tests
- [ ] Add logging configuration

## License

This project is open source.
