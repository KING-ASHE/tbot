import telebot

# මෙතනට ඔයාගේ Bot Token එක දාන්න
API_TOKEN = '7738385271:AAG9KoMEhyGk5iik2hM875Eew0EyiE9LFSI'

# මෙතනට ඔයාගේ Chat ID එක දාන්න (Number එකක් ලෙස)
ADMIN_ID = 7335765040 

bot = telebot.TeleBot(API_TOKEN)

# ඕනෑම පණිවිඩයක් (Text, Photo, Video, Document) ලැබුණු විට ක්‍රියාත්මක වේ
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def forward_to_admin(message):
    try:
        # බොට් හරහා පණිවිඩය එවූ පුද්ගලයාගේ විස්තර සමඟ ඇඩ්මින්ට Forward කිරීම
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        
        # (අවශ්‍ය නම් පමණක්) පණිවිඩය ලැබුණු බව පරිශීලකයාට දැන්වීමට පහත පේළිය පාවිච්චි කරන්න
        # bot.reply_to(message, "ඔබේ පණිවිඩය සාර්ථකව යොමු කෙරුණා!")
        
    except Exception as e:
        print(f"Error: {e}")

print("බොට් වැඩ කරන්න පටන් ගත්තා...")
bot.infinity_polling()
