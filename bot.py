import telebot

API_TOKEN = '7738385271:AAG9KoMEhyGk5iik2hM875Eew0EyiE9LFSI'
ADMIN_ID = 7335765040 

bot = telebot.TeleBot(API_TOKEN)

# /start command handler - forward කරන්නේ නෑ
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "හෙලෝ! ඔබේ පණිවිඩය එවන්න.")

# ඕනෑම පණිවිඩයක් ලැබුණු විට - /start හැර
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def forward_to_admin(message):
    # /start වගේ commands forward කරන්නේ නෑ
    if message.text and message.text.startswith(''):
        return
    
    try:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    except Exception as e:
        print(f"Error: {e}")

print("බොට් වැඩ කරන්න පටන් ගත්තා...")
bot.infinity_polling()