import telebot
import json
import os
import asyncio
from telethon import TelegramClient

API_TOKEN = '7738385271:AAG9KoMEhyGk5iik2hM875Eew0EyiE9LFSI'
ADMIN_ID = 7335765040

API_ID = '38963550'
API_HASH = '1e7e73506dd3e91f2c513240e701945d'
PHONE = '+94704608838'

bot = telebot.TeleBot(API_TOKEN)
client = TelegramClient('session', API_ID, API_HASH)

DATA_FILE = 'user_messages.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

forwarded_map = load_data()

# Async function එකක් හදලා loop එකෙන් run කරනවා
async def get_entity_id(identifier):
    try:
        entity = await client.get_entity(identifier)
        return entity.id
    except Exception as e:
        print(f"Get user error: {e}")
        return None

def get_user_id(identifier):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(get_entity_id(identifier))
    finally:
        loop.close()

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "හෙලෝ! ඔබේ පණිවිඩය එවන්න.")

@bot.message_handler(commands=['send'])
def handle_send(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        parts = message.text.split(' ', 2)
        
        if len(parts) < 3:
            bot.reply_to(message,
                "⚠️ නිවැරදි format එක:\n\n"
                "/send @username පණිවිඩය\n"
                "/send +94771234567 පණිවිඩය\n"
                "/send 123456789 පණිවිඩය")
            return
        
        identifier = parts[1]
        text_to_send = parts[2]
        
        bot.reply_to(message, "🔍 User හොයනවා...")

        if identifier.startswith('@') or identifier.startswith('+'):
            user_id = get_user_id(identifier)
        else:
            try:
                user_id = int(identifier)
            except ValueError:
                bot.reply_to(message, "❌ නිවැරදි format:\n/send @username msg\n/send +94xxxxxxxx msg\n/send 123456789 msg")
                return
        
        if user_id:
            bot.send_message(user_id, f"📩 පණිවිඩය:\n\n{text_to_send}")
            bot.reply_to(message, f"✅ පණිවිඩය යොමු කෙරුණා!\n👤 User ID: `{user_id}`")
        else:
            bot.reply_to(message,
                "❌ User හොයාගන්න බැරි උනා!\n\n"
                "කාරණා:\n"
                "- Username/Number නිවැරදි නෑ\n"
                "- ඒ user Telegram එකේ නෑ\n"
                "- Phone number නම් contact list එකේ නෑ")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message is not None)
def handle_admin_reply(message):
    try:
        replied_msg_id = str(message.reply_to_message.message_id)
        
        if replied_msg_id in forwarded_map:
            target_user_id = forwarded_map[replied_msg_id]
            
            if message.content_type == 'text':
                bot.send_message(target_user_id, f"📩 පණිවිඩය:\n\n{message.text}")
            elif message.content_type == 'photo':
                bot.send_photo(target_user_id, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'video':
                bot.send_video(target_user_id, message.video.file_id, caption=message.caption)
            elif message.content_type == 'document':
                bot.send_document(target_user_id, message.document.file_id, caption=message.caption)
            elif message.content_type == 'voice':
                bot.send_voice(target_user_id, message.voice.file_id)
            elif message.content_type == 'sticker':
                bot.send_sticker(target_user_id, message.sticker.file_id)

            bot.reply_to(message, "✅ පණිවිඩය සාර්ථකව යොමු කෙරුණා!")
        else:
            bot.reply_to(message, "❌ User හොයාගන්න බැරි උනා.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def forward_to_admin(message):
    if message.text and message.text.startswith('/'):
        return
    
    try:
        forwarded = bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        forwarded_map[str(forwarded.message_id)] = message.chat.id
        save_data(forwarded_map)
        
    except Exception as e:
        print(f"Error: {e}")

print("බොට් වැඩ කරන්න පටන් ගත්තා...")

# Client start කරනවා - OTP එන්න පුළුවන් first time
with client:
    client.loop.run_until_complete(client.start(phone=PHONE))
    client.loop.run_forever()
    
bot.infinity_polling()