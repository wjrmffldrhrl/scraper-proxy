import json
from app.lambda_function import lambda_handler

# 예시 데이터
get_event = {
    "httpMethod": "GET",
    "headers": {
        "Content-Type": "application/json"
    },
    "queryStringParameters": {
        "url": "https://www.youtube.com/watch?v=zx1FH6l1ZIM"
    },
    "body": None  # GET 요청의 경우 필요 없는 경우에 None을 할당
}

# post_event = {
#     "httpMethod": "POST",
#     "headers": {
#         "Content-Type": "application/json"
#     },
#     "queryStringParameters": {
#         "url": "https://example.com"
#     },
#     "body": json.dumps({"key": "value"})
# }

# 빈 컨텍스트 객체 (Test 용도)
context = {}


def main():
    # GET 요청 테스트
    print("Testing GET request:")
    response = lambda_handler(get_event, context)
    print(json.dumps(response, indent=4))

    # # POST 요청 테스트
    # print("Testing POST request:")
    # response = lambda_handler(post_event, context)
    # print(json.dumps(response, indent=4))


if __name__ == "__main__":
    main()