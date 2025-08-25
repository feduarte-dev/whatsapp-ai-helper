import requests

url = "https://807ad97e743e.ngrok-free.app/webhook"

payload = {
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "messages": [
                            {
                                "from": "5511999999999",
                                "text": {"body": "estou muito angustiado com as decisçoes do meu filho"}
                            }
                        ]
                    }
                }
            ]
        }
    ]
}

response = requests.post(url, json=payload)
print(response.json())
