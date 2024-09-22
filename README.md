# Lambda Proxy Server with Docker

This repository contains a sample AWS Lambda function for a proxy server that can be deployed using Docker.

## Files and Directories

- `app/`: Contains the Lambda function code.
  - `lambda_function.py`: Main handler for the Lambda function.
- `Dockerfile`: Docker configuration file to build the image.
- `requirements.txt`: Python dependencies.
- `entry.sh`: Optional entry point script (default is enough for most cases).
- `README.md`: This file.

## Deployment

To deploy this Lambda function using Docker, follow these steps:

1. **Build the Docker image**:
    ```sh
    docker build -t my-lambda-proxy .
    ```

2. **Test the Docker image locally** (optional):
    ```sh
    docker run -p 9000:8080 my-lambda-proxy
    ```

3. **Push the Docker image to Amazon ECR**:
    Follow the AWS documentation to push your Docker image to Amazon ECR.

4. **Deploy the Lambda function**:
    Configure your Lambda function to use the image from Amazon ECR.

## Usage

This Lambda function can proxy HTTP requests to a target URL provided as a query parameter.

- **GET request example**:
    ```sh
    curl -X GET "https://your-api-id.execute-api.your-region.amazonaws.com/your-stage?url=https://example.com"
    ```

- **POST request example**:
    ```sh
    curl -X POST "https://your-api-id.execute-api.your-region.amazonaws.com/your-stage?url=https://example.com" -d '{"key": "value"}'
    ```

## Testing

You can test the function locally with Docker using the Lambda Runtime Interface Emulator (RIE) provided by AWS:

```sh
docker run -p 9000:8080 my-lambda-proxy