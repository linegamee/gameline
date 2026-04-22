import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import time
import json
from datetime import datetime, timezone

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def save_user(user_id, username, first_name, last_name):
    users = load_users()
    user_id_str = str(user_id)
    
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    if user_id_str not in users:
        users[user_id_str] = {
            'id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name or '',
            'first_interaction': now,
            'last_interaction': now
        }
    else:
        users[user_id_str]['last_interaction'] = now
        if username and username != users[user_id_str].get('username'):
            users[user_id_str]['username'] = username
        if first_name and first_name != users[user_id_str].get('first_name'):
            users[user_id_str]['first_name'] = first_name
    
    save_users(users)
    print(f"✅ Сохранён: {user_id} ({username}) - {now}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    
    save_user(user_id, username, first_name, last_name)
    
    text = (f"Welcome, {first_name or 'Guest'}! Здесь ты найдешь все самые популярные игры — и не только🔥✅\n\n"
            "✅Подпишись на канал и получи полный доступ к играм👇")
    
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="ПОДПИСАТЬСЯ", url="https://t.me/+VV1URmD4IusxNWUx", style="success")
    keyboard.add(button)
    
    bot.send_message(user_id, text, reply_markup=keyboard)

@bot.message_handler(content_types=['photo'])
def get_photo_file_id(message):
    file_id = message.photo[-1].file_id
    bot.reply_to(message, f"`{file_id}`", parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    ADMIN_ID = 854916968
    
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ У тебя нет доступа.")
        return
    
    try:
        parts = message.text.replace('/broadcast', '', 1).strip().split('|')
        text = parts[0].strip()
        file_id = parts[1].strip()
        button_url = parts[2].strip()
    except:
        bot.reply_to(message, "❌ Формат: /broadcast Текст | file_id | ссылка")
        return
    
    users_dict = load_users()
    if not users_dict:
        bot.reply_to(message, "📭 Нет пользователей.")
        return
    
    users_ids = [int(uid) for uid in users_dict.keys()]
    
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="ПОЛУЧИТЬ БОНУС", url=button_url, style="success")
    button = InlineKeyboardButton(text="ИГРАТЬ", ur2=button_ur2, style="success")
    keyboard.add(button)
    
    bot.reply_to(message, f"🚀 Рассылка для {len(users_ids)} пользователей...")
    
    success = 0
    fail = 0
    
    for user_id in users_ids:
        try:
            bot.send_photo(user_id, file_id, caption=text, reply_markup=keyboard)
            success += 1
            time.sleep(0.1)
        except:
            fail += 1
    
    bot.reply_to(message, f"✅ Готово!\nОтправлено: {success}\nОшибок: {fail}")
  @bot.message_handler(commands=['stats'])
def stats(message):
    ADMIN_ID = 854916968
    if message.from_user.id != ADMIN_ID:
        return
    
    users = load_users()
    
    if not users:
        bot.reply_to(message, "📭 Нет пользователей.")
        return
    
    result = "📊 *Список пользователей:*\n\n"
    for uid, data in users.items():
        name = data.get('first_name', 'No name')
        username = data.get('username', '')
        last_seen = data.get('last_interaction', 'Unknown')
        username_str = f" (@{username})" if username else ""
        result += f"• {name}{username_str}\n  🆔 `{uid}`\n  🕐 {last_seen}\n\n"
    
    if len(result) > 4000:
        result = result[:4000] + "\n... (обрезано)"
    
    bot.send_message(message.chat.id, result, parse_mode='Markdown')

print("✅ Бот Game Line запущен!")
bot.infinity_polling()
