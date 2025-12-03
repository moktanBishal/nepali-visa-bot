import httpx
import google.generativeai as genai
import logging
import json
from config import Config

logger = logging.getLogger(__name__)

class WhatsAppClient:
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/v18.0/{Config.PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }

    async def send_text_message(self, to_phone_number: str, text: str):
        """Sends a text message to a WhatsApp user."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "text",
            "text": {"body": text},
        }
        await self._send_request(payload)

    async def send_reply_buttons(self, to_phone_number: str, text: str, buttons: dict):
        """
        Sends a message with up to 3 interactive reply buttons.
        buttons dict format: {"id1": "Title 1", "id2": "Title 2"}
        """
        rows = []
        for btn_id, btn_title in buttons.items():
            rows.append({
                "type": "reply",
                "reply": {
                    "id": btn_id,
                    "title": btn_title
                }
            })
            
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": text
                },
                "action": {
                    "buttons": rows
                }
            }
        }
        await self._send_request(payload)

    async def mark_as_read(self, message_id: str):
        """Marks a message as read."""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        await self._send_request(payload)

    async def _send_request(self, payload: dict):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to send WhatsApp message: {e.response.text}")
                return None
            except Exception as e:
                logger.error(f"Error sending WhatsApp request: {str(e)}")
                return None

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Optimized System Prompt for Nepali Work Visas in Europe (2025)
        self.system_instruction = """
You are 'Namaste Europe', an expert AI immigration consultant dedicated to helping Nepali citizens secure Work Visas for European countries (Schengen Zone, UK, Poland, Portugal, Malta, Croatia, etc.) for the year 2025.

YOUR CORE RULES:
1. **Language & Tone:**
   - **Auto-detection:** If the user writes in Nepali (Romanized or Devanagari), reply in clear, professional Nepali.
   - If the user writes in English, reply in English.
   - Always start with a warm greeting (e.g., "Namaste 🙏").
   - Use polite honorifics ("Tapai", "Hajur").

2. **Expertise (2025 Context):**
   - Focus on popular destinations for Nepalis: **Poland, Portugal, Malta, Croatia, Romania, and the UK.**
   - Explain specific visa types: Seasonal Work, EU Blue Card, National D-Type Visas.
   - Highlight 2025 changes: Digital submission trends, increased salary thresholds, and stricter document verification (VFS Global).
   - Mention the 'Demand Letter' requirement and the role of the Department of Foreign Employment (DOFE).

3. **Formatting for WhatsApp:**
   - Keep responses concise (max 150 words).
   - Use emojis (🇪🇺, 🇳🇵, 📄, ✅) to make text scannable.
   - Use bullet points for steps or requirements.
   - Do NOT use markdown bolding (asterisks) excessively as it can look messy on some older phones; use it only for headers.

4. **Safety & Ethics:**
   - **WARNING:** Aggressively warn users about 'Manpower' scams. Advise them to check if the agency is registered with the DOFE in Nepal (foreignemployment.gov.np).
   - **DISCLAIMER:** "I am an AI, not a lawyer or government official. Always verify with the official embassy or DOFE."

5. **Interaction Style:**
   - If the user says "Hi" or "Namaste", ask: "Which European country are you planning to work in? (Tapai kun desh jana chahanu hunchha?)"
   - Be helpful, encouraging, but realistic about processing times.
"""
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=self.system_instruction
        )

    async def generate_response(self, history: list, user_input: str) -> str:
        """
        Generates a response using Gemini 1.5 Flash.
        """
        try:
            chat = self.model.start_chat(history=history)
            response = await chat.send_message_async(user_input)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {str(e)}")
            return "Namaste! 🙏 I am currently experiencing high traffic. Please try again in a moment. (Maaf garnuhola, maile ahile uttar dina sakina.)"
