import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_token")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])

                if messages:
                    msg = messages[0]
                    from_number = msg.get("from")
                    
                    # Yalnız mətn mesajlarını emal edirik
                    if msg.get("type") == "text":
                        text_body = msg.get("text", {}).get("body", "").strip()

                        # Avtomatik Cavab Məntiqi
                        if text_body.lower() in ["salam", "salam!"]:
                            reply_text = "Aleykum salam! Növbə sistemi üçün 'Növbə' sözünü yazın."
                        elif text_body.lower() == "növbə":
                            reply_text = "Növbəniz qeydə alındı! Sizin növbə nömrəniz: #12"
                        else:
                            reply_text = f"Mesajınız alındı: '{text_body}'. Növbə götürmək üçün 'Növbə' yazın."

                        send_whatsapp_message(from_number, reply_text)

        return jsonify({"status": "success"}), 200
    return jsonify({"status": "not a whatsapp event"}), 404

def send_whatsapp_message(to_number, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Meta API Response: {response.status_code}, {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
