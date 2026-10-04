import random
import json
import os
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = "В8058954271:AAEUWsfWPmX45JugiBUczOLq7xxQhgWm3xQ"

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)

active_users = load_users()

# ========== ВІДПОВІДІ НА !апероль ==========
APEROL_RESPONSES = [
    "Офіціант приніс Вам апероль зі словами: «Пий, не обляпайся!»",
    "Приніс апероль, але додав секретний інгредієнт. Смакуй обережно.",
    "Офіціант поставив апероль і прошепотів: «Це останній, більше не буде».",
    "Приніс апероль і сказав: «За рахунок закладу... ну майже».",
    "Офіціант приніс апероль і додав: «Пий швидше, поки шеф не бачить».",
    "Поставив апероль перед Вами і суворо попередив: «Не розливай, це мистецтво».",
    "Приніс апероль і всміхнувся: «Зі спеціальним побажанням від кухні».",
    "Офіціант поставив келих і сказав: «Пий, а то {user} вже чекає свою чергу».",
    "Приніс апероль і додав: «Секретний інгредієнт — трохи поваги до офіціанта».",
    "Офіціант простягнув апероль зі словами: «На здоров’я, і не забудь чайові».",
    "Поставив апероль і тихо сказав: «Це не просто апероль. Це апероль з характером».",
    "Приніс напій і додав: «Пий повільно. {user} вже заздрить».",
    "Офіціант поставив келих і промовив: «Замовляв? Отримуй. Без питань».",
    "Приніс апероль і всміхнувся загадково: «Секретний інгредієнт — трохи хаосу».",
    "Офіціант поставив апероль і сказав: «Пий, поки {user} не встиг його стягнути».",
    "Приніс келих і додав: «Це апероль преміум. Бо звичайний вже закінчився».",
    "Офіціант простягнув напій зі словами: «Смакуй. І не питай, що я туди додав».",
    "Поставив апероль і суворо глянув: «Пий акуратно. Це не вода».",
    "Приніс апероль і сказав: «З особистим привітом від {user}».",
    "Офіціант поставив келих і тихо додав: «Секретний інгредієнт — трохи удачі».",
]

# ========== ВІДПОВІДІ НА !вкрав апероль ==========
STEAL_RESPONSES = [
    "Відвернуло увагу і тихенько вкрало апероль у {user}",
    "Поки {user} відволіклося — швидко замінило апероль на воду і забрало собі",
    "Скориставшись моментом, спритно вкрало апероль у {user}",
    "Відволікло {user} і тихенько прихопило апероль",
    "Поки {user} відійшло — підмінило апероль на звичайну воду і забрало собі",
    "Зробило вигляд, що нічого не сталося, і тихенько вкрало апероль у {user}",
    "Спритно підмінило напій у {user} і спокійно пішло далі",
    "Відвернуло увагу компанії і тихенько забрало апероль у {user}",
    "Поки {user} відволіклося — швидко випило трохи і долило водою",
    "Скориставшись моментом, непомітно вкрало апероль у {user}",
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = str(update.effective_chat.id)
    user = update.effective_user
    text = update.message.text.strip()
    text_lower = text.lower()

    # Запам'ятовуємо користувача
    if chat_id not in active_users:
        active_users[chat_id] = {}
    
    name = f"@{user.username}" if user.username else user.first_name
    active_users[chat_id][str(user.id)] = name
    save_users(active_users)

    # ----- Команда !апероль -----
    if text_lower.startswith("!апероль") or text_lower.startswith("!aperol"):
        response = random.choice(APEROL_RESPONSES)
        
        if "{user}" in response:
            users = list(active_users.get(chat_id, {}).values())
            target = random.choice(users) if users else "когось"
            response = response.format(user=target)
        
        await update.message.reply_text(response)
        return

    # ----- Команда !вкрав апероль -----
    if text_lower.startswith("!вкрав апероль") or text_lower.startswith("!вкрав апэроль"):
        
        # Шукаємо згадку @username
        mention = re.search(r'@(\w+)', text)
        
        if mention:
            target = f"@{mention.group(1)}"
        else:
            users = list(active_users.get(chat_id, {}).values())
            if not users:
                await update.message.reply_text("Поки немає кого красти...")
                return
            target = random.choice(users)

        response = random.choice(STEAL_RESPONSES).format(user=target)
        await update.message.reply_text(response)
        return

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущений і готовий...")
    app.run_polling()

if __name__ == "__main__":
    main()