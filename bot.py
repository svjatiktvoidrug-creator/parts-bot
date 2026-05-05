import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID = os.environ["GROUP_CHAT_ID"]

(REGISTER_LAST_NAME, REGISTER_FIRST_NAME, WAITING_STICKER_PHOTO, CHOOSE_CATEGORY,
 CHOOSE_IPHONE_MODEL, CHOOSE_IPHONE_PARTS, FREE_TEXT_PARTS, CONFIRM_ORDER,
 OTHER_PART_TEXT) = range(9)

# Моделі по 3 в ряд
IPHONE_MODELS_ROWS = [
    [("iphone_xr", "iPhone XR"), ("iphone_x", "iPhone X"), ("iphone_xs", "iPhone XS")],
    [("iphone_xs_max", "iPhone XS Max")],
    [("iphone_11", "iPhone 11"), ("iphone_11_pro", "iPhone 11 Pro"), ("iphone_11_pro_max", "iPhone 11 Pro Max")],
    [("iphone_12_mini", "iPhone 12 Mini"), ("iphone_12", "iPhone 12"), ("iphone_12_pro", "iPhone 12 Pro")],
    [("iphone_12_pro_max", "iPhone 12 Pro Max")],
    [("iphone_13_mini", "iPhone 13 Mini"), ("iphone_13", "iPhone 13"), ("iphone_13_pro", "iPhone 13 Pro")],
    [("iphone_13_pro_max", "iPhone 13 Pro Max")],
    [("iphone_14", "iPhone 14"), ("iphone_14_plus", "iPhone 14 Plus"), ("iphone_14_pro", "iPhone 14 Pro")],
    [("iphone_14_pro_max", "iPhone 14 Pro Max")],
    [("iphone_15", "iPhone 15"), ("iphone_15_plus", "iPhone 15 Plus"), ("iphone_15_pro", "iPhone 15 Pro")],
    [("iphone_15_pro_max", "iPhone 15 Pro Max")],
    [("iphone_16", "iPhone 16"), ("iphone_16_plus", "iPhone 16 Plus"), ("iphone_16_pro", "iPhone 16 Pro")],
    [("iphone_16_pro_max", "iPhone 16 Pro Max")],
    [("iphone_17", "iPhone 17"), ("iphone_17_air", "iPhone 17 Air"), ("iphone_17_pro", "iPhone 17 Pro")],
    [("iphone_17_pro_max", "iPhone 17 Pro Max")],
]

IPHONE_MODELS_DICT = {key: name for row in IPHONE_MODELS_ROWS for key, name in row}

# Запчастини з тестовими артикулами
IPHONE_PARTS = [
    ("part_display_orig",   "🖥 Дисплейний модуль (оригінал) — арт. DSP-001"),
    ("part_display_copy",   "🖥 Дисплейний модуль (копія) — арт. DSP-002"),
    ("part_glass",          "🔲 Скло екрану — арт. GLS-001"),
    ("part_touch",          "👆 Сенсор (тачскрін) — арт. TCH-001"),
    ("part_battery_orig",   "🔋 Акумулятор (оригінал) — арт. BAT-001"),
    ("part_battery_copy",   "🔋 Акумулятор (копія) — арт. BAT-002"),
    ("part_charger_port",   "🔌 Роз'єм зарядки — арт. CHG-001"),
    ("part_camera_main",    "📷 Основна камера — арт. CAM-001"),
    ("part_camera_front",   "🤳 Фронтальна камера — арт. CAM-002"),
    ("part_faceid",         "🔐 Модуль Face ID — арт. FID-001"),
    ("part_speaker_ear",    "🔈 Динамік розмовний — арт. SPK-001"),
    ("part_speaker_loud",   "🔊 Динамік гучний (нижній) — арт. SPK-002"),
    ("part_mic",            "🎙 Мікрофон — арт. MIC-001"),
    ("part_back_cover",     "🔧 Задня кришка / корпус — арт. CVR-001"),
    ("part_btn_power",      "⚡️ Кнопка Power — арт. BTN-001"),
    ("part_btn_volume",     "🔉 Кнопки гучності — арт. BTN-002"),
    ("part_btn_home",       "⬜️ Кнопка Home — арт. BTN-003"),
    ("part_vibro",          "📳 Вібромотор — арт. VIB-001"),
    ("part_proximity",      "🌡 Датчик наближення — арт. SNS-001"),
    ("part_antenna",        "📡 Шлейф антени — арт. ANT-001"),
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
    return ReplyKeyboardMarkup([[KeyboardButton("🛒 Замовити запчастину")]], resize_keyboard=True)


def build_models_keyboard():
    keyboard = []
    for row in IPHONE_MODELS_ROWS:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"model_{key}") for key, name in row])
    return InlineKeyboardMarkup(keyboard)


def build_parts_keyboard(selected):
    keyboard = []
    for part_id, part_name in IPHONE_PARTS:
        mark = "✅ " if part_id in selected else ""
        keyboard.append([InlineKeyboardButton(f"{mark}{part_name}", callback_data=f"toggle_{part_id}")])
    keyboard.append([InlineKeyboardButton("📝 Інше", callback_data="other_part")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад до вибору моделі", callback_data="back_to_models")])
    keyboard.append([InlineKeyboardButton("✔️ Підтвердити замовлення", callback_data="confirm_parts")])
    return InlineKeyboardMarkup(keyboard)


def build_order_summary(data):
    parts = data.get("parts_list", [])
    parts_text = "\n".join(f"  • {p}" for p in parts)
    model_line = f"📱 *Модель:* {data.get('iphone_model', '')}\n" if data.get("iphone_model") else ""
    return (
        "📋 *Перевірте ваше замовлення:*\n\n"
        f"👤 *Працівник:* {data.get('employee_name', '')}\n"
        f"🗂 *Категорія:* {data.get('category', '')}\n"
        f"{model_line}"
        f"🔧 *Запчастини:*\n{parts_text}\n\nВсе вірно?"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = context.bot_data.get("users", {})
    if user_id in users:
        await update.message.reply_text(f"👋 З поверненням, {users[user_id]}!", reply_markup=get_main_menu())
        return ConversationHandler.END
    await update.message.reply_text("👋 Вітаємо!\n\nВведіть ваше *прізвище*:", parse_mode="Markdown")
    return REGISTER_LAST_NAME


async def register_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_name"] = update.message.text.strip()
    await update.message.reply_text("Тепер введіть ваше *ім'я*:", parse_mode="Markdown")
    return REGISTER_FIRST_NAME


async def register_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.text.strip()
    last_name = context.user_data.get("last_name", "")
    full_name = f"{last_name} {first_name}"
    if "users" not in context.bot_data:
        context.bot_data["users"] = {}
    context.bot_data["users"][str(update.effective_user.id)] = full_name
    await update.message.reply_text(f"✅ Зареєстровано як *{full_name}*!", parse_mode="Markdown", reply_markup=get_main_menu())
    return ConversationHandler.END


async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = context.bot_data.get("users", {})
    if user_id not in users:
        await update.message.reply_text("⚠️ Спочатку введіть /start")
        return ConversationHandler.END
    context.user_data.clear()
    context.user_data["employee_name"] = users[user_id]
    context.user_data["selected_parts"] = []
    await update.message.reply_text("📸 Надішліть фото стікера з IMEI або серійним номером:")
    return WAITING_STICKER_PHOTO


async def receive_sticker_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ Надішліть саме фото стікера.")
        return WAITING_STICKER_PHOTO
    context.user_data["sticker_photo_id"] = update.message.photo[-1].file_id
    keyboard = [[InlineKeyboardButton(label, callback_data=key)] for key, label in CATEGORIES.items()]
    await update.message.reply_text("✅ Фото отримано!\n\nОберіть категорію:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_CATEGORY


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_key = query.data
    context.user_data["category"] = CATEGORIES[category_key]
    context.user_data["iphone_model"] = None
    if category_key == "cat_iphone":
        await query.edit_message_text("Оберіть модель iPhone:", reply_markup=build_models_keyboard())
        return CHOOSE_IPHONE_MODEL
    await query.edit_message_text(
        f"Категорія: *{CATEGORIES[category_key]}*\n\nОпишіть потрібні запчастини:",
        parse_mode="Markdown"
    )
    return FREE_TEXT_PARTS


async def choose_iphone_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    model_key = query.data.replace("model_", "")
    model_name = IPHONE_MODELS_DICT.get(model_key, model_key)
    context.user_data["iphone_model"] = model_name
    context.user_data["selected_parts"] = []
    await query.edit_message_text(
        f"Модель: *{model_name}*\n\nОберіть запчастини (можна декілька):",
        parse_mode="Markdown",
        reply_markup=build_parts_keyboard([])
    )
    return CHOOSE_IPHONE_PARTS


async def toggle_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_models":
        await query.edit_message_text("Оберіть модель iPhone:", reply_markup=build_models_keyboard())
        return CHOOSE_IPHONE_MODEL

    if query.data == "other_part":
        await query.edit_message_text(
            "📝 Напишіть що саме потрібно замовити (назва, артикул, або опис):"
        )
        return OTHER_PART_TEXT

    if query.data == "confirm_parts":
        selected = context.user_data.get("selected_parts", [])
        if not selected:
            await query.answer("⚠️ Оберіть хоча б одну запчастину!", show_alert=True)
            return CHOOSE_IPHONE_PARTS
        context.user_data["parts_list"] = [name for pid, name in IPHONE_PARTS if pid in selected]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Відправити замовлення", callback_data="send_order")],
            [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")]
        ])
        await query.edit_message_text(build_order_summary(context.user_data), parse_mode="Markdown", reply_markup=keyboard)
        return CONFIRM_ORDER

    part_id = query.data.replace("toggle_", "")
    selected = context.user_data.get("selected_parts", [])
    if part_id in selected:
        selected.remove(part_id)
    else:
        selected.append(part_id)
    context.user_data["selected_parts"] = selected
    await query.edit_message_text(
        f"Модель: *{context.user_data.get('iphone_model', '')}*\n\nОберіть запчастини:",
        parse_mode="Markdown",
        reply_markup=build_parts_keyboard(selected)
    )
    return CHOOSE_IPHONE_PARTS


async def other_part_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    other_text = update.message.text.strip()
    selected = context.user_data.get("selected_parts", [])
    parts_list = [name for pid, name in IPHONE_PARTS if pid in selected]
    parts_list.append(f"📝 Інше: {other_text}")
    context.user_data["parts_list"] = parts_list
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Відправити замовлення", callback_data="send_order")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")]
    ])
    await update.message.reply_text(build_order_summary(context.user_data), parse_mode="Markdown", reply_markup=keyboard)
    return CONFIRM_ORDER


async def free_text_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["parts_list"] = [update.message.text.strip()]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Відправити замовлення", callback_data="send_order")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_order")]
    ])
    await update.message.reply_text(build_order_summary(context.user_data), parse_mode="Markdown", reply_markup=keyboard)
    return CONFIRM_ORDER


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel_order":
        await query.edit_message_text("❌ Замовлення скасовано.")
        return ConversationHandler.END

    data = context.user_data
    parts_text = "\n".join(f"  • {p}" for p in data.get("parts_list", []))
    model_line = f"📱 Модель: {data.get('iphone_model', '')}\n" if data.get("iphone_model") else ""
    group_message = (
        "🛒 *НОВЕ ЗАМОВЛЕННЯ ЗАПЧАСТИН*\n\n"
        f"👤 Працівник: *{data.get('employee_name', '')}*\n"
        f"🗂 Категорія: {data.get('category', '')}\n"
        f"{model_line}"
        f"🔧 Запчастини:\n{parts_text}"
    )
    try:
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=data.get("sticker_photo_id"),
            caption=group_message,
            parse_mode="Markdown"
        )
        await query.edit_message_text("✅ *Замовлення відправлено!*", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.edit_message_text("⚠️ Помилка при відправці. Зверніться до адміністратора.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Скасовано.", reply_markup=get_main_menu())
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    reg_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTER_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_last_name)],
            REGISTER_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_first_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="registration",
        persistent=False,
    )

    order_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex("Замовити запчастину"), order_start),
        ],
        states={
            WAITING_STICKER_PHOTO: [MessageHandler(filters.PHOTO, receive_sticker_photo)],
            CHOOSE_CATEGORY: [CallbackQueryHandler(choose_category, pattern="^cat_")],
            CHOOSE_IPHONE_MODEL: [CallbackQueryHandler(choose_iphone_model, pattern="^model_")],
            CHOOSE_IPHONE_PARTS: [CallbackQueryHandler(toggle_part, pattern="^(toggle_|confirm_parts|other_part|back_to_models)")],
            OTHER_PART_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, other_part_text)],
            FREE_TEXT_PARTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, free_text_parts)],
            CONFIRM_ORDER: [CallbackQueryHandler(confirm_order, pattern="^(send_order|cancel_order)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="order",
        persistent=False,
        allow_reentry=True,
    )

    app.add_handler(reg_conv)
    app.add_handler(order_conv)

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
