import logging
import json
import redis.asyncio as redis
from fastapi import FastAPI, Request, Response, BackgroundTasks, HTTPException
from config import Config
from utils import WhatsAppClient, GeminiClient

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WhatsAppBot")

app = FastAPI()

# Initialize Clients
redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
whatsapp = WhatsAppClient()
gemini = GeminiClient()

# Constants
MAX_HISTORY_MESSAGES = 16
SESSION_TTL = 86400

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "Nepali Visa Bot"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == Config.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def webhook_handler(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            message = messages[0]
            background_tasks.add_task(process_message, message)
            
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error parsing webhook: {str(e)}")
        return {"status": "error", "detail": str(e)}

async def process_message(message: dict):
    try:
        user_phone = message["from"]
        message_type = message["type"]
        message_id = message["id"]
        
        await whatsapp.mark_as_read(message_id)
        
        if not await check_rate_limit(user_phone):
            # await whatsapp.send_text_message(user_phone, "Limit reached (30/hr).")
            return

        # Handle Reply Buttons first
        if message_type == "interactive":
            interaction = message["interactive"]
            if interaction["type"] == "button_reply":
                user_text = interaction["button_reply"]["title"] # Use button text as input
            else:
                return
        elif message_type == "text":
            user_text = message["text"]["body"]
        else:
            return

        # Check for "Start" or "Menu" command to show buttons
        if user_text.lower() in ["start", "menu", "hi", "hello", "namaste"]:
             buttons = {
                 "btn_poland": "Poland Visa 🇵🇱",
                 "btn_portugal": "Portugal Visa 🇵🇹",
                 "btn_uk": "UK Seasonal 🇬🇧"
             }
             await whatsapp.send_reply_buttons(user_phone, "Namaste! 🙏 Select a country to check 2025 Visa details:", buttons)
             # Do not generate AI response for the menu itself, wait for selection
             # But we might want to save this "Start" in history? 
             # Let's just return here to keep it simple interaction.
             return

        # Normal flow (AI Response)
        history_key = f"history:{user_phone}"
        raw_history = await redis_client.lrange(history_key, 0, -1)
        
        gemini_history = []
        if raw_history:
            for item in reversed(raw_history):
                try:
                    gemini_history.append(json.loads(item))
                except json.JSONDecodeError:
                    continue

        ai_response_text = await gemini.generate_response(gemini_history, user_text)
        
        await whatsapp.send_text_message(user_phone, ai_response_text)
        
        # Update History
        user_msg_obj = {"role": "user", "parts": [user_text]}
        model_msg_obj = {"role": "model", "parts": [ai_response_text]}
        
        await redis_client.lpush(history_key, json.dumps(user_msg_obj))
        await redis_client.lpush(history_key, json.dumps(model_msg_obj))
        await redis_client.ltrim(history_key, 0, MAX_HISTORY_MESSAGES - 1)
        await redis_client.expire(history_key, SESSION_TTL)

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

async def check_rate_limit(user_id: str) -> bool:
    """
    Rate limiter: 30 messages per hour (3600s).
    """
    key = f"rate_limit:{user_id}"
    try:
        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, Config.RATE_LIMIT_WINDOW)
            
        if current > Config.RATE_LIMIT_REQUESTS:
            return False
        return True
    except Exception as e:
        logger.error(f"Redis Rate Limit Error: {e}")
        return True
