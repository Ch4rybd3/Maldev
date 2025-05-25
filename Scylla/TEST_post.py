import requests
import json

url = "http://127.0.0.1:8000/"

data = {
    "hostname": "boy",
    "timestamp": "2025-05-24T13:02:01Z",
    "payload": {
        "key": "value",
        "data": [1, 2, 3]
    },
    "auth_key": "1887509308309418244689469339184520403722",
    "malware": "testmalware"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(f"Status Code: {response.status_code}")
print("Response:")
print(response.json())
