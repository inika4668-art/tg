# ТЕЛЕГРАМ-БОТ ДЛЯ ОТДЕЛА ГО и ЧС

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

# =====================================================
# ТВОЙ ТОКЕН (уже вставлен)
# =====================================================
TOKEN = "8628544046:AAEtIyUuGunwESzAmWpOOmfDIPTe50ZK_8k"

# =====================================================
# ТВОЙ ID (уже вставлен)
# =====================================================
CHAT_IDS = [
    811072430,  # твой Telegram ID
]

# Состояния для диалога
CHOOSING_CHS, ASKING_DISTRICT, ASKING_CUSTOM = range(3)

# Шаблоны сообщений для разных ЧС
TEMPLATES = {
    "1": "🔥 ПОЖАР",
    "2": "🌊 НАВОДНЕНИЕ", 
    "3": "☣️ ХИМИЧЕСКАЯ УГРОЗА",
}

# Команда /start — приветствие и меню
async def start(update: Update, context):
    await update.message.reply_text(
        "🚨 ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ ОПОВЕЩЕНИЯ ГО и ЧС 🚨\n\n"
        "Отправь цифру:\n"
        "1 — 🔥 Пожар\n"
        "2 — 🌊 Наводнение\n"
        "3 — ☣️ Химическая угроза\n"
        "4 — ✏️ Своё сообщение\n"
        "0 — ❌ Выйти"
    )
    return CHOOSING_CHS

# Обработка выбора пользователя
async def handle_chs_choice(update: Update, context):
    text = update.message.text
    context.user_data['chs_choice'] = text
    
    if text == "0":
        await update.message.reply_text("До свидания! Берегите себя!")
        return ConversationHandler.END
    elif text == "4":
        await update.message.reply_text("Введите текст оповещения:")
        return ASKING_CUSTOM
    elif text in ["1", "2", "3"]:
        await update.message.reply_text("Укажите район (например: Центральный):")
        return ASKING_DISTRICT
    else:
        await update.message.reply_text("Нажми 1, 2, 3, 4 или 0")
        return CHOOSING_CHS

# Отправка оповещения с шаблоном (пожар, наводнение и т.д.)
async def ask_district(update: Update, context):
    district = update.message.text
    chs_type = TEMPLATES.get(context.user_data['chs_choice'], "ЧС")
    
    message = f"🚨 ВНИМАНИЕ! {chs_type} в районе {district}! Следуйте инструкциям!"
    
    for chat_id in CHAT_IDS:
        await context.bot.send_message(chat_id=chat_id, text=message)
    
    await update.message.reply_text(f"✅ Оповещение отправлено!\n{message}")
    return ConversationHandler.END

# Отправка своего сообщения
async def ask_custom(update: Update, context):
    message = update.message.text
    
    for chat_id in CHAT_IDS:
        await context.bot.send_message(chat_id=chat_id, text=f"🚨 {message}")
    
    await update.message.reply_text(f"✅ Отправлено: {message}")
    return ConversationHandler.END

# Отмена операции
async def cancel(update: Update, context):
    await update.message.reply_text("Операция отменена")
    return ConversationHandler.END

# Главная функция — запускает бота
def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_CHS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chs_choice)],
            ASKING_DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_district)],
            ASKING_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_custom)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    print("✅ Бот запущен! Напиши ему /start в Телеграме")
    app.run_polling()

# Запускаем
if __name__ == "__main__":
    main()