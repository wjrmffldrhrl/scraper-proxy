import os
import json
import boto3
import concurrent.futures
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AWS_REGION = "us-west-2" # Deployment region
MIN_PROXY_NUMBER = 1
MAX_PROXY_NUMBER = 1000
MAX_WORKERS = 20 # Concurrency

# Lock for printing to avoid garbled output
print_lock = threading.Lock()

def init_aws_client():
    """Initializes AWS Lambda client."""
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not aws_access_key_id or not aws_secret_access_key:
        if os.path.exists("aws_access_key.json"):
            with open("aws_access_key.json", "r") as f:
                creds = json.load(f)
                aws_access_key_id = creds.get("aws_access_key_id")
                aws_secret_access_key = creds.get("aws_secret_access_key")

    if not aws_access_key_id or not aws_secret_access_key:
        with print_lock:
            print("Error: AWS credentials not found.")
        return None

    # Create a session to ensure thread safety if needed, though client is generally fine
    session = boto3.Session(
        region_name=AWS_REGION,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    return session.client('lambda')

def test_proxy(client, proxy_id):
    function_name = f"proxy-{proxy_id}"
    target_url = "http://httpbin.org/ip"

    payload = {
        "httpMethod": "GET",
        "headers": {
            "target-url": target_url
        }
    }

    result_msg = ""
    is_success = False

    try:
        response = client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        response_payload = json.loads(response["Payload"].read())

        if "body" in response_payload:
            body_str = response_payload["body"]
            try:
                body_json = json.loads(body_str)
                origin_ip = body_json.get("origin")
                result_msg = f"{function_name} -> SUCCESS (IP: {origin_ip})"
                is_success = True
            except json.JSONDecodeError:
                # Truncate long body
                short_body = (body_str[:50] + '...') if len(body_str) > 50 else body_str
                # If 503, it's a failure from the target or lambda
                if "503" in body_str:
                     result_msg = f"{function_name} -> FAILED (503 Service Unavailable)"
                else:
                     result_msg = f"{function_name} -> SUCCESS (Non-JSON body: {short_body})"
                     is_success = True
        else:
             result_msg = f"{function_name} -> FAILED (Unexpected format: {response_payload})"

    except client.exceptions.ResourceNotFoundException:
        result_msg = f"{function_name} -> FAILED (Function not found)"
    except Exception as e:
        result_msg = f"{function_name} -> FAILED (Error: {str(e)})"

    with print_lock:
        print(result_msg)

    return is_success

def main():
    print("=== AWS Lambda Proxy Tester (Multithreaded) ===")
    print(f"Region: {AWS_REGION}")
    print(f"Workers: {MAX_WORKERS}")

    # We initialize client once. boto3 client is thread-safe.
    client = init_aws_client()
    if not client:
        return

    success_count = 0
    total_count = 0

    # Use ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        futures = {executor.submit(test_proxy, client, i): i for i in range(MIN_PROXY_NUMBER, MAX_PROXY_NUMBER + 1)}

        for future in concurrent.futures.as_completed(futures):
            total_count += 1
            if future.result():
                success_count += 1

    print("\n=== Test Summary ===")
    print(f"Total Proxies: {total_count}")
    print(f"Success: {success_count}")
    print(f"Failed: {total_count - success_count}")

if __name__ == "__main__":
    main()
