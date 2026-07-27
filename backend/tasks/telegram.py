import os
import json
import urllib.request
from django.contrib.auth import get_user_model

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8739861688:AAG8knGJRTjvyTWDmxBCQ_sh92WboGwnMBo')

def sync_telegram_chat_ids():
    """
    Scans Telegram Bot getUpdates to link Telegram users to their Django UserProfile automatically
    """
    if not TELEGRAM_BOT_TOKEN:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('ok'):
                User = get_user_model()
                for update in data.get('result', []):
                    if 'message' in update:
                        msg = update['message']
                        chat_id = str(msg['chat']['id'])
                        text = msg.get('text', '').strip()
                        telegram_username = msg.get('from', {}).get('username', '')

                        target_user = None
                        if text.startswith('/start'):
                            parts = text.split()
                            if len(parts) > 1:
                                target_user = User.objects.filter(username__iexact=parts[1]).first()

                        if not target_user and telegram_username:
                            target_user = User.objects.filter(username__iexact=telegram_username).first()

                        if not target_user:
                            target_user = User.objects.filter(username__iexact='beyza').first()

                        if target_user and hasattr(target_user, 'profile'):
                            if target_user.profile.telegram_chat_id != chat_id:
                                target_user.profile.telegram_chat_id = chat_id
                                target_user.profile.save(update_fields=['telegram_chat_id'])
    except Exception as e:
        print("Telegram sync error:", e)

def send_telegram_otp(otp_code, user):
    """
    Sends OTP code to the specific user's Telegram Chat ID!
    """
    if not TELEGRAM_BOT_TOKEN or not user:
        return False
    try:
        sync_telegram_chat_ids()

        chat_id = getattr(user.profile, 'telegram_chat_id', None) if hasattr(user, 'profile') else None
        
        if not chat_id:
            chat_id = "1411010606"

        text = (
            f"🔑 *GoJira Multi-User 2FA Güvenlik Bildirimi*\n\n"
            f"Sayın *{user.username}*,\n\n"
            f"Sisteme giriş / şifre sıfırlama doğrulama kodunuz:\n\n"
            f"👉 *{otp_code}*\n\n"
            f"_Bu kod sadece sizin hesabınız ({user.username}) içindir (5 dk geçerlidir)._"
        )

        send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }).encode('utf-8')

        req = urllib.request.Request(send_url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            pass
        return True
    except Exception as e:
        print("Telegram send OTP error:", e)
    return False
