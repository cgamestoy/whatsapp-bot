import requests

url = "http://127.0.0.1:5000/webhook"

payload = {
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "messages": [
                            {
                                "from": "5491112345678",
                                "type": "text",
                                "text": {
                                    "body": "hola"
                                }
                            }
                        ]
                    }
                }
            ]
        }
    ]
}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print("Respuesta JSON:", response.json())