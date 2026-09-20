import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ.get("BOT_TOKEN")

main_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🇨🇳 Урок дня", callback_data="lesson")],
    [
        InlineKeyboardButton("🔁 Повторение", callback_data="repeat"),
        InlineKeyboardButton("📊 Прогресс", callback_data="progress"),
    ],
])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🇨🇳 你好! Добро пожаловать!\n\n"
        "Я твой персональный преподаватель китайского языка. 🧠\n\n"
        "Каждый день мы будем изучать новые слова, "
        "тренировать произношение и повторять пройденное.\n\n"
        "🔥 Начинаем с HSK 1.\n"
        "⏱ Урок займёт примерно 10–15 минут.\n\n"
        "Выбери действие 👇"
    )

    await update.message.reply_text(text, reply_markup=main_keyboard)


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "lesson":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➡️ Следующее слово", callback_data="word2")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="menu")],
        ])

        await query.edit_message_text(
            "🇨🇳 УРОК 1 — Знакомство\n\n"
            "Сегодня начнём с самого важного.\n\n"
            "1️⃣ 你好\n"
            "Pinyin: nǐ hǎo\n"
            "Перевод: Привет 👋\n\n"
            "🗣 Произношение примерно:\n"
            "«ни хао»\n\n"
            "Нажми ниже, когда запомнишь 👇",
            reply_markup=keyboard,
        )

    elif query.data == "word2":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧠 Проверить себя", callback_data="quiz1")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="menu")],
        ])

        await query.edit_message_text(
            "2️⃣ 谢谢\n\n"
            "Pinyin: xièxie\n"
            "Перевод: Спасибо 🙏\n\n"
            "🗣 Примерно: «сье-сье»\n\n"
            "Пример:\n"
            "谢谢你 — xièxie nǐ\n"
            "Спасибо тебе.\n\n"
            "Теперь маленький тест 👇",
            reply_markup=keyboard,
        )

    elif query.data == "quiz1":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Привет", callback_data="wrong")],
            [InlineKeyboardButton("Спасибо", callback_data="correct")],
            [InlineKeyboardButton("До свидания", callback_data="wrong")],
        ])

        await query.edit_message_text(
            "🧠 ТЕСТ\n\n"
            "Что означает 谢谢?",
            reply_markup=keyboard,
        )

    elif query.data == "correct":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➡️ Продолжить урок", callback_data="finish")],
        ])

        await query.edit_message_text(
            "✅ Правильно!\n\n"
            "谢谢 = Спасибо 🙏\n\n"
            "Отличное начало! 🇨🇳",
            reply_markup=keyboard,
        )

    elif query.data == "wrong":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Попробовать ещё раз", callback_data="quiz1")],
        ])

        await query.edit_message_text(
            "❌ Пока нет.\n\n"
            "Подсказка: 谢谢 говорят, когда хотят поблагодарить человека. 😉",
            reply_markup=keyboard,
        )

    elif query.data == "finish":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="menu")],
        ])

        await query.edit_message_text(
            "🎉 Первый мини-урок завершён!\n\n"
            "Сегодня ты выучил:\n\n"
            "你好 — nǐ hǎo — привет\n"
            "谢谢 — xièxie — спасибо\n\n"
            "🔥 Серия: 1 день\n"
            "⭐ +10 XP\n\n"
            "明天见! — До завтра! 🇨🇳",
            reply_markup=keyboard,
        )

    elif query.data == "repeat":
        await query.edit_message_text(
            "🔁 Повторение\n\n"
            "Здесь будут появляться слова, которые тебе нужно повторить.\n\n"
            "Сначала пройди первый урок 🇨🇳",
            reply_markup=main_keyboard,
        )

    elif query.data == "progress":
        await query.edit_message_text(
            "📊 ТВОЙ ПРОГРЕСС\n\n"
            "🇨🇳 Уровень: HSK 1\n"
            "📚 Изучено слов: 0\n"
            "⭐ XP: 0\n"
            "🔥 Серия: 0 дней\n\n"
            "Это только начало 🚀",
            reply_markup=main_keyboard,
        )

    elif query.data == "menu":
        await query.edit_message_text(
            "🇨🇳 Главное меню\n\n"
            "Что будем делать?",
            reply_markup=main_keyboard,
        )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Chinese bot started 🇨🇳")
    app.run_polling()


if __name__ == "__main__":
    main()
