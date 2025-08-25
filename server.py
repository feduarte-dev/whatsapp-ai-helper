import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from tools.answer import ai_answer

load_dotenv()
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN  = 'christian-token-123'
app = FastAPI()

def send_whatsapp_message(to, text):
    """Envia mensagem de volta via API do WhatsApp"""
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("Resposta enviada:", r.json())

@app.post("/webhook")
async def webhook(request: Request):
    """Recebe mensagens do WhatsApp e responde via OpenAI"""
    data = await request.json()
    response = "⚠️ Ocorreu um erro, tente novamente."

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user_text = message["text"]["body"]
        user_number = message["from"]

        print(f"Mensagem recebida de {user_number}: {user_text}")

        response = ai_answer(user_text)
        send_whatsapp_message(user_number, response)

    except Exception as e:
        print("Erro no webhook:", e)
    return {"status": "received", "data": response}

# --- Webhook Verification (GET) ---
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        return PlainTextResponse(content="Erro de verificação", status_code=403)