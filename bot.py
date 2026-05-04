import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID", "YOUR_GROUP_CHAT_ID_HERE")

# Conversation states
(
    REGISTER_LAST_NAME, REGISTER_FIRST_NAME,
    WAITING_STICKER_PHOTO, CHOOSE_CATEGORY,
    CHOOSE_IPHONE_MODEL, CHOOSE_IPHONE_PARTS,
    FREE_TEXT_PARTS, CONFIRM_ORDER
) = range(8)

# iPhone models
IPHONE_MODELS = {
    "iphone_x_series": "📱 iPhone X / XS / XS Max / XR",
    "iphone_11_series": "📱 iPhone 11 / 11 Pro / 11 Pro Max",
    "iphone_12_series": "📱 iPhone 12 / 12 Mini / 12 Pro / 12 Pro Max",
    "iphone_13_series": "📱 iPhone 13 / 13 Mini / 13 Pro / 13 Pro Max",
    "iphone_14_series": "📱 iPhone 14 / 14 Plus / 14 Pro / 14 Pro Max",
    "iphone_15_series": "📱 iPhone 15 / 15 Plus / 15 Pro / 15 Pro Max",
    "iphone_16_series": "📱 iPhone 16 / 16 Plus / 16 Pro / 16 Pro Max",
    "iphone_17_series": "📱 iPhone 17 / 17 Air / 17 Pro / 17 Pro Max",
}

# Parts list for iPhone
IPHONE_PARTS = [
    ("part_display_orig", "🖥 Дисплейний модуль (оригінал)"),
    ("part_display_copy", "🖥 Дисплейний модуль (копія)"),
    ("part_glass", "🔲 Скло екрану"),
    ("part_touch", "👆 Сенсор (тачскрін)"),
    ("part_battery_orig", "🔋 Акумулятор (оригінал)"),
    ("part_battery_copy", "🔋 Акумулятор (копія)"),
    ("part_charger_port", "🔌 Роз'єм зарядки"),
    ("part_camera_main", "📷 Основна камера"),
    ("part_camera_front", "🤳 Фронтальна камера"),
    ("part_faceid", "🔐 Модуль Face ID"),
    ("part_speaker_ear", "🔈 Динамік розмовний"),
    ("part_speaker_loud", "🔊 Динамік гучний (нижній)"),
    ("part_mic", "🎙 Мікрофон"),
    ("part_back_cover", "🔧 Задня кришка / корпус"),
    ("part_btn_power", "⚡️ Кнопка Power"),
    ("part_btn_volume", "🔉 Кнопки гучності"),
    ("part_btn_home", "⬜️ Кнопка Home"),
    ("part_vibro", "📳 Вібромотор"),
    ("part_proximity", "🌡 Датчик наближення"),
    ("part_antenna", "📡 Шлейф антени"),
]

CATEGORIES = {
    "cat_iphone": "📱 Запчастини iPhone",
    "cat_ipad": "📟 Запчастини iPad",
    "cat_macbook": "💻 Запчастини MacBook",
    "cat_watch": "⌚️ Запчастини Apple Watch",
    "cat_android": "🤖 Андроїди",
    "cat_other": "📦 Інше",
}


def get_main_menu():
    keyboard = [[KeyboardButton("🛒 Замовити запчастину")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users = context.bot_data.get("users", {})

    if str(user_id) in users:
        name = users[str(user_id)]
        await update.message.reply_text(
            f"👋 З поверненням, {name}!\nНатисніть кнопку нижче щоб зробити замовлення.",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "👋 Вітаємо в боті замовлення запчастин!\n\n"
            "Для початку роботи потрібна реєстрація.\n\n"
            "Введіть ваше *прізвище*:",
            parse_mode="Markdown"
        )
        return REGISTER_LAST_NAME


async def register_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_name"] = update.message.text.strip()
    await update.message.reply_text("Тепер введіть ваше *ім'я*:", parse_mode="Markdown")
    return REGISTER_FIRST_NAME


async def register_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.text.strip()
    last_name = context.user_data["last_name"]
    full_name = f"{last_name} {first_name}"
    user_id = str(update.effective_user.id)

    if "users" not in context.bot_data:
        context.bot_data["users"] = {}
    context.bot_data["users"][user_id] = full_name

    await update.message.reply_text(
        f"✅ Реєстрація успішна!\n\nВаше ім'я: *{full_name}*\n\nТепер ви можете робити замовлення.",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END


async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = context.bot_data.get("users", {})

    if user_id not in users:
        await update.message.reply_text(
            "⚠️ Спочатку потрібно зареєструватися. Введіть /start"
        )
        return ConversationHandler.END

    context.user_data.clear()
    context.user_data["employee_name"] = users[user_id]
    context.user_data["selected_parts"] = []

    await update.message.reply_text(
        "📸 Надішліть фото стікера з IMEI або серійним номером пристрою:"
    )
    return WAITING_STICKER_PHOTO


async def receive_sticker_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ Будь ласка, надішліть саме *фото* стікера.", parse_mode="Markdown")
        return WAITING_STICKER_PHOTO

    context.user_data["sticker_photo_id"] = update.message.photo[-1].file_id

    keyboard = []
    for key, label in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(label, callback_data=key)])

    await update.message.reply_text(
        "✅ Фото отримано!\n\nОберіть категорію запчастин:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSE_CATEGORY


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_key = query.data
    context.user_data["category"] = CATEGORIES[category_key]

    if category_key == "cat_iphone":
        keyboard = []
        for key, label in IPHONE_MODELS.items():
            keyboard.append([InlineKeyboardButton(label, callback_data=key)])
        await query.edit_message_text(
            "Оберіть модель iPhone:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSE_IPHONE_MODEL
    else:
        await query.edit_message_text(
            f"Категорія: *{CATEGORIES[category_key]}*\n\n"
            "Опишіть потрібні запчастини текстом (модель пристрою, що саме потрібно):",
            parse_mode="Markdown"
        )
        return FREE_TEXT_PARTS


async def choose_iphone_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    model_key = query.data
    context.user_data["iphone_model"] = IPHONE_MODELS[model_key]
    context.user_data["selected_parts"] = []

    await query.edit_message_text(
        f"Модель: *{IPHONE_MODELS[model_key]}*\n\n"
        "Оберіть потрібні запчастини (можна декілька):",
        parse_mode="Markdown",
        reply_markup=build_parts_keyboard([])
    )
    return CHOOSE_IPHONE_PARTS


def build_parts_keyboard(selected):
    keyboard = []
    for part_id, part_name in IPHONE_PARTS:
        mark = "✅ " if part_id in selected else ""
        keyboard.append([InlineKeyboardButton(f"{mark}{part_name}", callback_data=f"toggle_{part_id}")])
    keyboard.append([InlineKeyboardButton("✔️ Підтвердити замовлення", callback_data="confirm_parts")])
    return InlineKeyboardMarkup(keyboard)


async def toggle_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_parts":
        selected = context.user_data.get("selected_parts", [])
        if not selected:
            await query.answer("⚠️ Оберіть хоча б одну запчастину!", show_alert=True)
            return CHOOSE_IPHONE_PARTS

        parts_names = [name for pid, name in IPHONE_PARTS if pid in selected]
        context.user_data["parts_list"] = parts_names

        summary = build_order_summary(context.user_data)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Відправити замовлення", callback_data="send_order")],
            [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")]
        ])
        await query.edit_message_text(summary, parse_mode="Markdown", reply_markup=keyboard)
        return CONFIRM_ORDER

    part_id = query.data.replace("toggle_", "")
    selected = context.user_data.get("selected_parts", [])

    if part_id in selected:
        selected.remove(part_id)
    else:
        selected.append(part_id)
    context.user_data["selected_parts"] = selected

    model = context.user_data.get("iphone_model", "")
    await query.edit_message_text(
        f"Модель: *{model}*\n\nОберіть потрібні запчастини (можна декілька):",
        parse_mode="Markdown",
        reply_markup=build_parts_keyboard(selected)
    )
    return CHOOSE_IPHONE_PARTS


async def free_text_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["parts_list"] = [update.message.text.strip()]
    summary = build_order_summary(context.user_data)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Відправити замовлення", callback_data="send_order")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")]
    ])
    await update.message.reply_text(summary, parse_mode="Markdown", reply_markup=keyboard)
    return CONFIRM_ORDER


def build_order_summary(data):
    parts = data.get("parts_list", [])
    parts_text = "\n".join(f"  • {p}" for p in parts)
    model_line = f"📱 *Модель:* {data.get('iphone_model', '')}\n" if data.get("iphone_model") else ""

    return (
        "📋 *Перевірте ваше замовлення:*\n\n"
        f"👤 *Працівник:* {data.get('employee_name', '')}\n"
        f"🗂 *Категорія:* {data.get('category', '')}\n"
        f"{model_line}"
        f"🔧 *Запчастини:*\n{parts_text}\n\n"
        "Все вірно?"
    )


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_order":
        await query.edit_message_text("❌ Замовлення скасовано.")
        return ConversationHandler.END

    data = context.user_data
    parts = data.get("parts_list", [])
    parts_text = "\n".join(f"  • {p}" for p in parts)
    model_line = f"📱 Модель: {data.get('iphone_model', '')}\n" if data.get("iphone_model") else ""

    group_message = (
        "🛒 *НОВЕ ЗАМОВЛЕННЯ ЗАПЧАСТИН*\n\n"
        f"👤 Працівник: *{data.get('employee_name', '')}*\n"
        f"🗂 Категорія: {data.get('category', '')}\n"
        f"{model_line}"
        f"🔧 Запчастини:\n{parts_text}"
    )

    try:
        photo_id = data.get("sticker_photo_id")
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=photo_id,
            caption=group_message,
            parse_mode="Markdown"
        )
        await query.edit_message_text(
            "✅ *Замовлення успішно відправлено!*\n\nВаш менеджер отримав заявку.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error sending to group: {e}")
        await query.edit_message_text(
            "⚠️ Виникла помилка при відправці. Зверніться до адміністратора."
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Скасовано.", reply_markup=get_main_menu())
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Registration conversation
    reg_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTER_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_last_name)],
            REGISTER_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_first_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Order conversation
    order_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🛒 Замовити запчастину$"), order_start)],
        states={
            WAITING_STICKER_PHOTO: [MessageHandler(filters.PHOTO | filters.TEXT, receive_sticker_photo)],
            CHOOSE_CATEGORY: [CallbackQueryHandler(choose_category, pattern="^cat_")],
            CHOOSE_IPHONE_MODEL: [CallbackQueryHandler(choose_iphone_model, pattern="^iphone_")],
            CHOOSE_IPHONE_PARTS: [CallbackQueryHandler(toggle_part, pattern="^(toggle_|confirm_parts)")],
            FREE_TEXT_PARTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, free_text_parts)],
            CONFIRM_ORDER: [CallbackQueryHandler(confirm_order, pattern="^(send_order|cancel_order)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(reg_handler)
    app.add_handler(order_handler)

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
