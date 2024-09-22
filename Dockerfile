# Base image
FROM public.ecr.aws/lambda/python:3.9

# Install the necessary dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy the function code
COPY app ./app

# Set the CMD to your handler
CMD ["app.lambda_function.lambda_handler"]