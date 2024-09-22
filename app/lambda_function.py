import json
import requests
from requests.exceptions import RequestException

def lambda_handler(event, context):
    method = event['httpMethod']
    headers = event['headers']
    body = event['body']
    target_url = event['queryStringParameters'].get('url')

    if not target_url:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'The query parameter "url" is required.'})
        }

    try:
        if method == 'GET':
            response = requests.get(target_url, headers=headers)
        elif method == 'POST':
            response = requests.post(target_url, headers=headers, data=body)
        else:
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'HTTP method {method} not supported'})
            }

        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.text
        }

    except RequestException as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }