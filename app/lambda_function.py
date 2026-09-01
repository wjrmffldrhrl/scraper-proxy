import base64
import json
import logging
import requests

# Configure logging at global scope
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Hop-by-hop headers that should be removed
HOP_BY_HOP_HEADERS = {
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade',
    'content-encoding', 'content-length', 'host'
}

def lambda_handler(event, context):
    # Extract the target URL from headers
    headers = event.get('headers', {}) or {}
    # Convert all header keys to lowercase for consistent handling
    headers = {k.lower(): v for k, v in headers.items()}

    target_url = headers.get('target-url')
    logger.info(f"targetURL: {target_url}")

    if not target_url:
        return {
            "statusCode": 400,
            "body": "Missing target-url header"
        }

    # Extract HTTP method and body
    method = event.get('httpMethod', 'GET')
    is_base64_encoded = event.get('isBase64Encoded', False)
    body = event.get('body')

    # Decode body if it is base64 encoded
    if body and is_base64_encoded:
        try:
            body = base64.b64decode(body)
        except Exception as e:
            logger.error(f"Error decoding base64 body: {e}")
            return {
                "statusCode": 400,
                "body": "Failed to decode base64 body"
            }
    elif body:
        # If body is string but we need bytes for requests
        body = body.encode('utf-8')

    # Prepare headers for the outgoing request
    # Filter out hop-by-hop headers and the special target-url header
    outgoing_headers = {}
    for k, v in headers.items():
        if k.lower() not in HOP_BY_HOP_HEADERS and k.lower() != 'target-url':
            outgoing_headers[k] = v

    try:
        # Make the HTTP request
        # Using verify=False can be dangerous, but useful for scraping sometimes.
        # Defaulting to standard behavior (verify=True) is safer unless requested otherwise.
        response = requests.request(
            method=method,
            url=target_url,
            headers=outgoing_headers,
            data=body,
            timeout=30 # Add a reasonable timeout
        )

        # Prepare response headers
        response_headers = {}
        for k, v in response.headers.items():
            if k.lower() not in HOP_BY_HOP_HEADERS:
                response_headers[k] = v

        # Encode the response body to base64
        response_body = base64.b64encode(response.content).decode('utf-8')

        return {
            "statusCode": response.status_code,
            "headers": response_headers,
            "body": response_body,
            "isBase64Encoded": True
        }

    except requests.RequestException as e:
        logger.error(f"Error making HTTP request: {e}")
        return {
            "statusCode": 502, # Bad Gateway is more appropriate for upstream errors
            "body": f"Failed to make HTTP request: {str(e)}"
        }