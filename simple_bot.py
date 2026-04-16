# ТЕЛЕГРАМ-БОТ ДЛЯ ОТДЕЛА ГО и ЧС
# Версия с автоматическим добавлением всех пользователей

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

TOKEN = "8628544046:AAEtIyUuGunwESzAmWpOOmfDIPTe50ZK_8k"

# =====================================================
# СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ (заполняется автоматически)
# =====================================================
all_users = []  # Сюда будут добавляться все, кто написал /start

# Состояния для диалога
CHOOSING_CHS, ASKING_DISTRICT, ASKING_CUSTOM = range(3)

# Шаблоны сообщений для разных ЧС
TEMPLATES = {
    "1": "🔥 ПОЖАР",
    "2": "🌊 НАВОДНЕНИЕ", 
    "3": "☣️ ХИМИЧЕСКАЯ УГРОЗА",
}

# Команда /start — приветствие и добавление пользователя
async def start(update: Update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Добавляем пользователя в список, если его там ещё нет
    if user_id not in all_users:
        all_users.append(user_id)
        print(f"➕ Добавлен новый пользователь: {user_name} (ID: {user_id})")
        print(f"📊 Всего пользователей: {len(all_users)}")
    
    await update.message.reply_text(
        "🚨 ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ ОПОВЕЩЕНИЯ ГО и ЧС 🚨\n\n"
        "Ты добавлен в список получателей оповещений!\n\n"
        "Отправь цифру:\n"
        "1 — 🔥 Пожар\n"
        "2 — 🌊 Наводнение\n"
        "3 — ☣️ Химическая угроза\n"
        "4 — ✏️ Своё сообщение\n"
        "0 — ❌ Выйти"
    )
    return CHOOSING_CHS

# Команда /stats — показать статистику (только для админа)
async def stats(update: Update, context):
    user_id = update.effective_user.id
    # Твой ID (админ) — может смотреть статистику
    if user_id == 811072430:  # твой ID
        await update.message.reply_text(
            f"📊 СТАТИСТИКА БОТА:\n"
            f"👥 Всего пользователей: {len(all_users)}\n"
            f"📝 Список ID: {all_users}"
        )
    else:
        await update.message.reply_text("❌ У тебя нет прав для этой команды.")

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
    
    # Отправляем ВСЕМ пользователям из списка
    if len(all_users) == 0:
        await update.message.reply_text("❌ Нет пользователей для оповещения!")
        return ConversationHandler.END
    
    sent_count = 0
    for user_id in all_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            sent_count += 1
        except Exception as e:
            print(f"❌ Ошибка отправки пользователю {user_id}: {e}")
    
    await update.message.reply_text(
        f"✅ Оповещение отправлено!\n"
        f"📨 Получили: {sent_count} из {len(all_users)} пользователей\n"
        f"📢 Текст: {message}"
    )
    return ConversationHandler.END

# Отправка своего сообщения
async def ask_custom(update: Update, context):
    message = update.message.text
    
    if len(all_users) == 0:
        await update.message.reply_text("❌ Нет пользователей для оповещения!")
        return ConversationHandler.END
    
    sent_count = 0
    for user_id in all_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"🚨 {message}")
            sent_count += 1
        except Exception as e:
            print(f"❌ Ошибка отправки пользователю {user_id}: {e}")
    
    await update.message.reply_text(
        f"✅ Оповещение отправлено!\n"
        f"📨 Получили: {sent_count} из {len(all_users)} пользователей"
    )
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
    app.add_handler(CommandHandler("stats", stats))  # Команда для статистики
    
    print("✅ Бот запущен!")
    print("📝 Все новые пользователи будут автоматически добавлены в список рассылки")
    app.run_polling()

if __name__ == "__main__":
    main()
