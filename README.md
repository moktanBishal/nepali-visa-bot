# 🇳🇵 Nepali Visa Bot (WhatsApp 2025)

> A production-ready WhatsApp chatbot that provides AI-powered visa advice for Nepali citizens. Features **Gemini 1.5 Flash**, **Redis Memory**, and **Official Meta Cloud API**.

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)

## ✨ Features
- **Smart AI**: Powered by Google Gemini 1.5 Flash (Fast & Free tier friendly).
- **Bilingual**: Automatically replies in **Nepali** (if user types Devanagari/Roman) or **English**.
- **Context Aware**: Remembers your conversation (up to 8 turns) using Redis.
- **Interactive**: Sends "Reply Buttons" for easy navigation.
- **Spam Protection**: Limits users to 30 messages/hour.
- **No Tunneling**: Works directly on Render/Railway (no ngrok needed).

---

## 🚀 Deployment Guide (5 Minutes)

### Step 1: Create Meta (WhatsApp) App
1. Go to [Meta for Developers](https://developers.facebook.com/) and log in.
2. Click **"My Apps"** -> **"Create App"**.
3. Select **"Other"** -> **"Business"**.
4. Give it a name (e.g., `NepaliVisaBot`) and create.
5. On the App Dashboard, scroll down to find **"WhatsApp"** and click **"Set up"**.
6. Select a Business Account (or create a test one).
7. **IMPORTANT**: In the API Setup page, copy:
   - **Temporary Access Token** (We will use this for testing. For production, create a System User).
   - **Phone Number ID**.
   - **Test Phone Number** (Use this to message yourself first).

### Step 2: Get Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Click **"Get API Key"** -> **"Create API Key"**.
3. Copy the key string (starts with `AIza...`).

### Step 3: Deploy (Choose One)

#### Option A: Render (Free & Easy)
1. Fork/Push this code to your GitHub.
2. Go to [Render.com](https://render.com/) -> **New** -> **Blueprint**.
3. Connect your repo.
4. Render will detect `render.yaml` and ask for Environment Variables. Fill them:
   - `WHATSAPP_TOKEN`: Paste from Step 1.
   - `PHONE_NUMBER_ID`: Paste from Step 1.
   - `GEMINI_API_KEY`: Paste from Step 2.
   - `WHATSAPP_VERIFY_TOKEN`: Create a secret (e.g., `nepal123`).
5. Click **Apply**. Render will deploy the Web Service and Redis automatically.

#### Option B: Railway
1. Push code to GitHub.
2. Open [Railway](https://railway.app/) -> **New Project** -> **Deploy from GitHub**.
3. Add a **Redis** service (Right click -> Database -> Redis).
4. Go to Settings -> **Variables** and add the same variables as above.

### Step 4: Connect Webhook
1. Once deployed, copy your app's URL (e.g., `https://nepali-visa-bot.onrender.com`).
2. Go back to **Meta Developer Portal** -> **WhatsApp** -> **Configuration**.
3. Click **"Edit"** next to Webhook.
4. **Callback URL**: `https://<YOUR_APP_URL>/webhook`
5. **Verify Token**: Enter the `WHATSAPP_VERIFY_TOKEN` you set in Step 3 (e.g., `nepal123`).
6. Click **Verify and Save**.
7. Under "Webhook Fields", click **"Manage"** and subscribe to **`messages`**.

### Step 5: Test!
1. Add the **Test Phone Number** (from Meta dashboard) to your WhatsApp contacts.
2. Send a message: **"Namaste"** or **"Start"**.
3. You should see a Button Menu! 
4. Ask: "How to apply for Poland seasonal visa?"

---

## 🛠️ Configuration (.env)

| Variable | Description |
| :--- | :--- |
| `WHATSAPP_TOKEN` | Meta API Access Token |
| `PHONE_NUMBER_ID` | Meta Phone Number ID (Found in API Setup) |
| `WHATSAPP_VERIFY_TOKEN` | Custom password for webhook verification |
| `GEMINI_API_KEY` | Google AI Studio Key |
| `REDIS_URL` | Auto-filled by Render/Railway |

## 🧩 Project Structure
- `main.py`: Core FastAPI app & Webhook logic.
- `utils.py`: Handles WhatsApp sending & Gemini AI generation.
- `config.py`: Settings & Environment variables.
- `render.yaml`: Deployment blueprint.

## 🇳🇵 Example Conversation
**User**: Namaste
**Bot**: [Buttons: Poland Visa 🇵🇱 | Portugal Visa 🇵🇹]
**User**: (Taps Poland)
**Bot**: *Namaste! For Poland Seasonal Work Visa in 2025...*
**User**: k salary kati huncha?
**Bot**: *Poland ma seasonal visa ko salary lagbhag 4,300 PLN (approx 1.4 Lakhs NPR) huncha...*