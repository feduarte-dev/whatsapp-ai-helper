from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from tools.answer import ai_answer

app = FastAPI()
VERIFY_TOKEN  = 'christian-token-123'

@app.post("/webhook")
async def webhook_test(request: Request):
    """Webhook de teste sem enviar pro WhatsApp"""
    data = await request.json()
    response = []

    try:
        messages = data.get("entry", [])[0].get("changes", [])[0].get("value", {}).get("messages", [])
        for message in messages:
            user_text = message.get("text", {}).get("body", "")
            user_number = message.get("from", "desconhecido")

            print(f"Mensagem recebida de {user_number}: {user_text}")
            resposta = ai_answer(user_text)
            print(f"Resposta gerada: {resposta}\n")
            response.append({"from": user_number, "resposta": resposta})

    except Exception as e:
        print("Erro no webhook de teste:", e)

    return {"status": "received", "respostas": response}

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
