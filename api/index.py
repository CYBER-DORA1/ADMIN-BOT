import telebot
from telebot import types
from flask import Flask, request
import os

TOKEN = 'ඔබේ_BOT_TOKEN_එක'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# රටවල් පෙන්වන Inline Keyboard එක
def country_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    countries = [
        ("🇦🇿 Azerbaijan(+994)", "aze"),
        ("🇨🇩 Congo (+243)", "congo"),
        ("🇪🇬 Egypt (+20)", "egypt"),
        ("🇰🇪 Kenya (+254)", "kenya"),
        ("🇸🇦 Saudi Arabia (+966)", "saudi"),
        ("🇸🇱 Sierra Leone (+232)", "sierra"),
        ("🇹🇯 Tajikistan (+992)", "taji")
    ]
    
    for text, callback in countries:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback))
    
    # පතුලේ ඇති අමතර බොත්තම
    markup.add(types.InlineKeyboardButton("🌎 Available Countries: 7", callback_data="none"))
    return markup

# පහළින් ඇති ස්ථිර Buttons (Reply Keyboard)
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('📞 Get Number'), types.KeyboardButton('📊 Active Numbers'))
    return markup

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "🌎 **Choose your country** 👇", 
        reply_markup=country_markup(), 
        parse_mode="Markdown"
    )
    # පහළ menu එකත් පෙන්වන්න අවශ්‍ය නම්:
    bot.send_message(message.chat.id, "Main Menu", reply_markup=main_menu())

# Button එකක් එබූ විට සිදුවන දේ (Callback query)
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "aze":
        bot.answer_callback_query(call.id, "ඔබ තෝරාගත්තේ Azerbaijan")
        bot.send_message(call.message.chat.id, "🇦🇿 Azerbaijan අංක සඳහා සූදානම් වෙමින්...")
    # අනෙක් රටවල් සඳහාද මෙලෙසම ලිවිය හැක

@app.route("/")
def webhook():
    bot.remove_webhook()
    # මෙතනට ඔබේ Vercel URL එක අනිවාර්යයෙන් දෙන්න
    bot.set_webhook(url='https://ඔබේ-vercel-app-නම.vercel.app/' + TOKEN)
    return "Webhook set correctly!", 200
