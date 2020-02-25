import requests
print(requests.get("http://127.0.0.1:8000/page/user?id=1").text)