import telebot
from telebot import types
from flask import Flask, request
import os

TOKEN = '8444081815:AAEKxRr0Bnw63qroONRbJ0n1DZJCLsmXblE'
ADMIN_ID = 7065070369  # ඔබේ Telegram User ID එක මෙතනට දාන්න
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# රටවල් අනුව අංක ගබඩා කරන තැන
numbers_store = {
    "aze": [], "congo": [], "egypt": [], "kenya": [], "saudi": [], "sierra": [], "taji": []
}

# රටවල් තෝරන මෙනුව
def country_markup(purpose="view"):
    markup = types.InlineKeyboardMarkup(row_width=1)
    countries = [
        ("🇦🇿 Azerbaijan(+994)", f"{purpose}_aze"),
        ("🇨🇩 Congo (+243)", f"{purpose}_congo"),
        ("🇪🇬 Egypt (+20)", f"{purpose}_egypt"),
        ("🇰🇪 Kenya (+254)", f"{purpose}_kenya"),
        ("🇸🇦 Saudi Arabia (+966)", f"{purpose}_saudi"),
        ("🇸🇱 Sierra Leone (+232)", f"{purpose}_sierra"),
        ("🇹🇯 Tajikistan (+992)", f"{purpose}_taji")
    ]
    for text, callback in countries:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌎 **Choose your country** 👇", reply_markup=country_markup("view"), parse_mode="Markdown")

# /addnumber command එක (Admin ට පමණයි)
@bot.message_handler(commands=['addnumber'])
def add_number_start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "අංක එකතු කිරීමට අවශ්‍ය රට තෝරන්න:", reply_markup=country_markup("add"))
    else:
        bot.reply_to(message, "ඔබට මෙම command එක භාවිතා කළ නොහැක.")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # View Numbers (පරිශීලකයා රටක් තෝරාගත් විට)
    if call.data.startswith("view_"):
        country_code = call.data.split("_")[1]
        nums = numbers_store.get(country_code, [])
        if not nums:
            bot.send_message(call.message.chat.id, "දැනට අංක කිසිවක් නොමැත.")
        else:
            msg = "\n".join([f"{i+1}. {n}" for i, n in enumerate(nums)])
            bot.send_message(call.message.chat.id, f"ලබාගත හැකි අංක:\n\n{msg}\n\n✅ Waiting for OTP...")

    # Add Numbers (Admin රටක් තෝරාගත් විට)
    elif call.data.startswith("add_"):
        country_code = call.data.split("_")[1]
        msg = bot.send_message(call.message.chat.id, f"දැන් {country_code} සඳහා අංකය ඇතුළත් කරන්න:")
        bot.register_next_step_handler(msg, save_number, country_code)

def save_number(message, country_code):
    new_num = message.text
    numbers_store[country_code].append(new_num)
    bot.send_message(message.chat.id, f"සාර්ථකයි! {new_num} අංකය {country_code} වෙත එකතු කරන ලදී.")

# Vercel Webhook Setup
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://ඔබේ-vercel-app-නම.vercel.app/' + TOKEN)
    return "Webhook set correctly!", 200
