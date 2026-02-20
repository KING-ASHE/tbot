import telebot
import json
import os
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ResolvePhoneRequest

API_TOKEN = '7738385271:AAG9KoMEhyGk5iik2hM875Eew0EyiE9LFSI'
ADMIN_ID = 7335765040

# Telegram API credentials - https://my.telegram.org වලින් ගන්න
API_ID = '38963550'
API_HASH = '1e7e73506dd3e91f2c513240e701945d'
PHONE = '+94704608838'  # +94xxxxxxxxx format

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

# Phone number එකෙන් Telegram User ID ගන්නවා
def get_user_id_by_phone(phone_number):
    try:
        with client:
            result = client(ResolvePhoneRequest(phone_number))
            return result.users[0].id
    except Exception as e:
        return None

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "හෙලෝ! ඔබේ පණිවිඩය එවන්න.")

# /sendphone command - phone number එකෙන් message යවනවා
# විදිහ: /sendphone +94xxxxxxxxx ඔයාගේ පණිවිඩය
@bot.message_handler(commands=['sendphone'])
def handle_send_phone(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        parts = message.text.split(' ', 2)
        
        if len(parts) < 3:
            bot.reply_to(message,
                "⚠️ නිවැරදි format එක:\n"
                "/sendphone <number> <පණිවිඩය>\n\n"
                "උදාහරණ:\n"
                "/sendphone +94771234567 හෙලෝ!")
            return
        
        phone_number = parts[1]
        text_to_send = parts[2]
        
        bot.reply_to(message, "🔍 User හොයනවා...")
        
        user_id = get_user_id_by_phone(phone_number)
        
        if user_id:
            bot.send_message(user_id, f"\n\n{text_to_send}")
            bot.reply_to(message, f"✅ {phone_number} ට පණිවිඩය Send කෙරුණා!\n👤 User ID: {user_id}")
        else:
            bot.reply_to(message, 
                "❌ User හොයාගන්න බැරි උනා!\n\n"
                "කාරණා:\n"
                "- Number එක Telegram එකේ නෑ\n"
                "- ඒ user ඔයාගේ contact list එකේ නෑ")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# /send command - user id එකෙන් message යවනවා
@bot.message_handler(commands=['send'])
def handle_send(message):
    if message.chat.id != ADMIN_ID:
        return
    
    try:
        parts = message.text.split(' ', 2)
        
        if len(parts) < 3:
            bot.reply_to(message,
                "⚠️ නිවැරදි format එක:\n"
                "/send <user_id> <පණිවිඩය>\n\n"
                "උදාහරණ:\n"
                "/send 123456789 හෙලෝ!")
            return
        
        target_user_id = int(parts[1])
        text_to_send = parts[2]
        
        bot.send_message(target_user_id, f"\n\n{text_to_send}")
        bot.reply_to(message, f"✅ User {target_user_id} ට පණිවිඩය Send කෙරුණා!")
        
    except ValueError:
        bot.reply_to(message, "❌ User ID එක වැරදි.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message is not None)
def handle_admin_reply(message):
    try:
        replied_msg_id = str(message.reply_to_message.message_id)
        
        if replied_msg_id in forwarded_map:
            target_user_id = forwarded_map[replied_msg_id]
            
            if message.content_type == 'text':
                bot.send_message(target_user_id, f"\n\n{message.text}")
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

            bot.reply_to(message, "✅ පණිවිඩය සාර්ථකව Send කෙරුණා!")
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

print("Bot Started...")
client.start(phone=PHONE)
bot.infinity_polling()