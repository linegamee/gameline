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
            'username': username or '',
            'first_name': first_name or '',
            'last_name': last_name or '',
            'first_interaction': now,
            'last_interaction': now
        }
        print(f"➕ Новый пользователь: {user_id} ({username})")
    else:
        users[user_id_str]['last_interaction'] = now
        if username and username != users[user_id_str].get('username'):
            users[user_id_str]['username'] = username
        if first_name and first_name != users[user_id_str].get('first_name'):
            users[user_id_str]['first_name'] = first_name
        print(f"🔄 Обновлён: {user_id} ({username})")
    
    save_users(users)
    print(f"✅ Сохранён: {user_id} ({username}) - {now}")
    
    updated_users = load_users()
    print(f"📊 Всего пользователей в файле: {len(updated_users)}")

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
    button = InlineKeyboardButton(text="ПОДПИСАТЬСЯ", url="https://t.me/+VV1URmD4IusxNWUx" , style="success")
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
        args = message.text.replace('/broadcast', '', 1).strip()
        if not args:
            raise ValueError("Нет аргументов")
        
        parts = args.split('|')
        if len(parts) < 3:
            raise ValueError("Недостаточно аргументов")
            
        text = parts[0].strip()
        file_id = parts[1].strip()
        button_url = parts[2].strip()
    except Exception as e:
        bot.reply_to(message, f"❌ Формат: /broadcast Текст | file_id | ссылка\nОшибка: {str(e)}")
        return
    
    users_dict = load_users()
    print(f"📊 Загружено пользователей: {len(users_dict)}")
    
    if not users_dict:
        bot.reply_to(message, "📭 Нет пользователей в базе.")
        return
    
    users_ids = [int(uid) for uid in users_dict.keys()]
    print(f"👥 ID пользователей: {users_ids}")
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    button2 = InlineKeyboardButton(text="ИГРАТЬ", url=button_url , style="success")
    keyboard.add(button1)
    
    bot.reply_to(message, f"🚀 Начинаю рассылку для {len(users_ids)} пользователей...")
    
    success = 0
    fail = 0
    
    for user_id in users_ids:
        try:
            bot.send_photo(user_id, file_id, caption=text, reply_markup=keyboard)
            success += 1
            print(f"✅ Отправлено пользователю {user_id}")
            time.sleep(0.1)
        except Exception as e:
            fail += 1
            print(f"❌ Ошибка при отправке {user_id}: {str(e)}")
    
    bot.reply_to(message, f"✅ Рассылка завершена!\n📤 Отправлено: {success}\n❌ Ошибок: {fail}")

@bot.message_handler(commands=['stats'])
def stats(message):
    ADMIN_ID = 854916968
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Нет доступа")
        return
    
    users = load_users()
    
    if not users:
        bot.reply_to(message, "📭 Нет пользователей в базе.")
        return
    
    total = len(users)
    
    # Отправляем общее количество пользователей отдельным сообщением
    total_msg = f"📊 *ОБЩЕЕ КОЛИЧЕСТВО ПОЛЬЗОВАТЕЛЕЙ:*\n👥 `{total}` пользователей"
    bot.send_message(message.chat.id, total_msg, parse_mode='Markdown')
    
    # Если пользователей мало, показываем всех
    if total <= 50:
        result = "━━━━━━━━━━━━━━━━━━━━━\n\n📋 *ПОЛНЫЙ СПИСОК ПОЛЬЗОВАТЕЛЕЙ:*\n\n"
        for uid, data in users.items():
            name = data.get('first_name', 'No name')
            username = data.get('username', '')
            last_seen = data.get('last_interaction', 'Unknown')
            first_seen = data.get('first_interaction', 'Unknown')
            username_str = f" (@{username})" if username else ""
            result += f"👤 *{name}*{username_str}\n"
            result += f"🆔 `{uid}`\n"
            result += f"📅 Первый раз: `{first_seen}`\n"
            result += f"🕐 Последний раз: `{last_seen}`\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            if len(result) > 3800:
                bot.send_message(message.chat.id, result, parse_mode='Markdown')
                result = ""
        
        if result:
            bot.send_message(message.chat.id, result, parse_mode='Markdown')
    else:
        # Если пользователей много, показываем последних 10 активных
        recent_msg = "━━━━━━━━━━━━━━━━━━━━━\n\n📋 *ПОСЛЕДНИЕ 10 АКТИВНЫХ ПОЛЬЗОВАТЕЛЕЙ:*\n\n"
        
        # Сортируем по последней активности
        sorted_users = sorted(users.items(), key=lambda x: x[1].get('last_interaction', ''), reverse=True)
        
        for uid, data in sorted_users[:10]:
            name = data.get('first_name', 'No name')
            username = data.get('username', '')
            last_seen = data.get('last_interaction', 'Unknown')
            username_str = f" (@{username})" if username else ""
            recent_msg += f"👤 *{name}*{username_str}\n"
            recent_msg += f"🆔 `{uid}`\n"
            recent_msg += f"🕐 Последний раз: `{last_seen}`\n"
            recent_msg += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        bot.send_message(message.chat.id, recent_msg, parse_mode='Markdown')
        
        # Добавляем информацию о первом пользователе
        first_user = min(users.items(), key=lambda x: x[1].get('first_interaction', ''))
        uid, data = first_user
        name = data.get('first_name', 'No name')
        first_seen = data.get('first_interaction', 'Unknown')
        
        first_info = f"🏆 *САМЫЙ ПЕРВЫЙ ПОЛЬЗОВАТЕЛЬ:*\n👤 {name}\n🆔 `{uid}`\n📅 Зарегистрирован: `{first_seen}`"
        bot.send_message(message.chat.id, first_info, parse_mode='Markdown')

print("✅ Бот Game Line запущен!")
print(f"📁 Файл пользователей: {USERS_FILE}")
print("🤖 Команды: /start, /stats (только админ), /broadcast (только админ)")
bot.infinity_polling()
