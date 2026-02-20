import telebot
import json
import os

API_TOKEN = '7738385271:AAG9KoMEhyGk5iik2hM875Eew0EyiE9LFSI'
ADMIN_ID = 7335765040

bot = telebot.TeleBot(API_TOKEN)

# JSON file path
DATA_FILE = 'user_messages.json'

# JSON file එකෙන් data load කිරීම
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            # JSON keys string වලින් int වලට convert කරනවා
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    return {}

# JSON file එකට data save කිරීම
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Startup වෙලාවේ data load කරනවා
user_messages = load_data()

# /start command handler
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "හෙලෝ! ඔබේ පණිවිඩය එවන්න.")

# Admin reply handler
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message is not None)
def handle_admin_reply(message):
    try:
        replied_msg_id = message.reply_to_message.message_id
        
        target_user_id = None
        for user_id, msg_id in user_messages.items():
            if msg_id == replied_msg_id:
                target_user_id = user_id
                break
        
        if target_user_id:
            # Admin reply - text, photo, video, document හෝ ඕනෑම content type
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
            bot.reply_to(message, "❌ User හොයාගන්න බැරි උනා. Forward වූ message එකට reply කරන්න.")
            
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, f"❌ Error: {e}")

# User messages forward කිරීම
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def forward_to_admin(message):
    if message.text and message.text.startswith('/'):
        return
    
    try:
        forwarded = bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        
        # User id සහ forwarded message id save කරනවා
        user_messages[message.chat.id] = forwarded.message_id
        save_data(user_messages)
        
    except Exception as e:
        print(f"Error: {e}")

print("බොට් වැඩ කරන්න පටන් ගත්තා...")
bot.infinity_polling()