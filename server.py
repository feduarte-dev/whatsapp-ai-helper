import os
import requests
import openai
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from tools.answer import ai_answer

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = "christian-token-123"
NGROK_URL = os.getenv("NGROK_URL")

app = FastAPI()


def send_whatsapp_message(to, text):
    """Sends whatsapp text message """
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
    print("Message text sent:", r.json())


def send_whatsapp_audio(to, audio_url):
    """Sends whatsapp audio message"""
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {"link": audio_url}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("Audio sent:", r.json())


def get_media_url(media_id):
    """Get temporary URL from whatsapp media_ID"""
    url = f"https://graph.facebook.com/v22.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    resp = requests.get(url, headers=headers).json()
    return resp["url"]


def transcribe_audio(media_url):
    """Download whatapp audio and transcript it"""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    r = requests.get(media_url, headers=headers)

    temp_path = "temp_audio.ogg"
    with open(temp_path, "wb") as f:
        f.write(r.content)

    with open(temp_path, "rb") as f:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text


def generate_tts_audio(text):
    """Generate audio from IA answer"""
    speech = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    output_dir = "audio_responses"
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, "response.mp3")
    with open(file_path, "wb") as f:
        f.write(speech.read()) 

    public_url = f"{NGROK_URL}/{file_path}"
    return public_url


@app.post("/webhook")
async def webhook(request: Request):
    """Get message from whatsapp and answers with AI"""
    data = await request.json()
    response = "⚠️ Ocorreu um erro, tente novamente."

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user_number = message["from"]

        if "text" in message:
            user_text = message["text"]["body"]
            print(f"Texto recebido: {user_text}")

            response = ai_answer(user_text)
            send_whatsapp_message(user_number, response)

        elif "audio" in message:
            audio_id = message["audio"]["id"]
            audio_url = get_media_url(audio_id)
            user_text = transcribe_audio(audio_url)
            print(f"Áudio transcrito: {user_text}")

            response_text = ai_answer(user_text)
            audio_public_url = generate_tts_audio(response_text)
            send_whatsapp_audio(user_number, audio_public_url)

    except Exception as e:
        print("Erro no webhook:", e)

    return {"status": "received", "data": response}

@app.get("/webhook")
async def verify(request: Request):
    """URL for whatsapp check project API"""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        return PlainTextResponse(content="Erro de verificação", status_code=403)
