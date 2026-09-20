import os
import json
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ.get("BOT_TOKEN")

DATA_FILE = Path("progress.json")

# =========================
# УРОКИ
# =========================

LESSONS = [
    {
        "title": "Знакомство 👋",
        "words": [
            ("你好", "nǐ hǎo", "Привет"),
            ("谢谢", "xiè xie", "Спасибо"),
            ("再见", "zài jiàn", "До свидания"),
            ("我", "wǒ", "Я"),
            ("你", "nǐ", "Ты"),
        ],
        "quiz": [
            ("Что означает 你好?", ["Привет", "Спасибо", "Пока"], 0),
            ("Как сказать «Спасибо»?", ["再见", "谢谢", "你好"], 1),
            ("Что означает 我?", ["Ты", "Я", "Мы"], 1),
        ],
    },
    {
        "title": "Числа 🔢",
        "words": [
            ("一", "yī", "Один"),
            ("二", "èr", "Два"),
            ("三", "sān", "Три"),
            ("四", "sì", "Четыре"),
            ("五", "wǔ", "Пять"),
        ],
        "quiz": [
            ("Что означает 三?", ["Один", "Три", "Пять"], 1),
            ("Как будет «два»?", ["二", "四", "五"], 0),
            ("Что означает 五?", ["Пять", "Три", "Четыре"], 0),
        ],
    },
    {
        "title": "Еда 🍜",
        "words": [
            ("水", "shuǐ", "Вода"),
            ("茶", "chá", "Чай"),
            ("米饭", "mǐ fàn", "Рис"),
            ("苹果", "píng guǒ", "Яблоко"),
            ("咖啡", "kā fēi", "Кофе"),
        ],
        "quiz": [
            ("Что означает 水?", ["Вода", "Чай", "Рис"], 0),
            ("Как будет «чай»?", ["咖啡", "茶", "苹果"], 1),
            ("Что означает 苹果?", ["Рис", "Кофе", "Яблоко"], 2),
        ],
    },
]


# =========================
# ПРОГРЕСС
# =========================

def load_data():
    if not DATA_FILE.exists():
        return {}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_user(user_id):
    data = load_data()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {
            "lesson": 0,
            "word": 0,
            "quiz": 0,
            "xp": 0,
            "streak": 1,
        }
        save_data(data)

    return data, data[uid]


# =========================
# КНОПКИ
# =========================

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇨🇳 Урок дня", callback_data="lesson")],
        [
            InlineKeyboardButton("🧠 Тест", callback_data="quiz"),
            InlineKeyboardButton("📊 Прогресс", callback_data="progress"),
        ],
        [InlineKeyboardButton("🔁 Повторение", callback_data="repeat")],
    ])


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🇨🇳 你好! Добро пожаловать!\n\n"
        "Я твой персональный преподаватель китайского языка. 🧠\n\n"
        "Каждый день будем учить новые слова, "
        "тренироваться и проходить мини-тесты.\n\n"
        "🎯 Цель: постепенно пройти HSK 1.\n"
        "⏱ 10–15 минут в день.\n\n"
        "Выбирай действие 👇"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard()
    )


# =========================
# УРОК
# =========================

async def lesson(query):
    data, user = get_user(query.from_user.id)

    lesson_index = min(user["lesson"], len(LESSONS) - 1)
    current = LESSONS[lesson_index]

    user["word"] = 0
    save_data(data)

    await show_word(query, current, 0)


async def show_word(query, lesson, index):
    word, pinyin, translation = lesson["words"][index]

    text = (
        f"🇨🇳 {lesson['title']}\n\n"
        f"Слово {index + 1}/{len(lesson['words'])}\n\n"
        f"🔤 {word}\n"
        f"🗣 Pinyin: {pinyin}\n"
        f"🇷🇺 {translation}\n\n"
        "Прочитай вслух 3 раза. 🔊"
    )

    if index + 1 < len(lesson["words"]):
        keyboard = [[
            InlineKeyboardButton(
                "➡️ Следующее слово",
                callback_data=f"word_{index + 1}"
            )
        ]]
    else:
        keyboard = [[
            InlineKeyboardButton(
                "🧠 Пройти тест",
                callback_data="quiz"
            )
        ]]

    keyboard.append([
        InlineKeyboardButton("🏠 Главное меню", callback_data="menu")
    ])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# ТЕСТ
# =========================

async def show_quiz(query, question_index=0):
    data, user = get_user(query.from_user.id)

    lesson_index = min(user["lesson"], len(LESSONS) - 1)
    current = LESSONS[lesson_index]

    if question_index >= len(current["quiz"]):
        user["xp"] += 30

        if user["lesson"] < len(LESSONS) - 1:
            user["lesson"] += 1

        user["quiz"] = 0
        save_data(data)

        await query.edit_message_text(
            "🎉 Урок завершён!\n\n"
            "Ты получил +30 XP ⭐\n\n"
            "Следующий урок разблокирован. 🔓",
            reply_markup=main_keyboard()
        )
        return

    question, answers, correct = current["quiz"][question_index]

    buttons = []

    for i, answer in enumerate(answers):
        buttons.append([
            InlineKeyboardButton(
                answer,
                callback_data=f"answer_{question_index}_{i}_{correct}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("🏠 Главное меню", callback_data="menu")
    ])

    await query.edit_message_text(
        f"🧠 Вопрос {question_index + 1}/{len(current['quiz'])}\n\n"
        f"{question}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================
# CALLBACK
# =========================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data

    if action == "menu":
        await query.edit_message_text(
            "🇨🇳 Главное меню\n\nЧто будем делать? 👇",
            reply_markup=main_keyboard()
        )

    elif action == "lesson":
        await lesson(query)

    elif action.startswith("word_"):
        index = int(action.split("_")[1])

        data, user = get_user(query.from_user.id)
        lesson_index = min(user["lesson"], len(LESSONS) - 1)
        current = LESSONS[lesson_index]

        user["word"] = index
        save_data(data)

        await show_word(query, current, index)

    elif action == "quiz":
        await show_quiz(query, 0)

    elif action.startswith("answer_"):
        _, question_index, selected, correct = action.split("_")

        question_index = int(question_index)
        selected = int(selected)
        correct = int(correct)

        if selected == correct:
            data, user = get_user(query.from_user.id)
            user["xp"] += 10
            save_data(data)

            await query.answer(
                "✅ Правильно! +10 XP",
                show_alert=True
            )

            await show_quiz(query, question_index + 1)

        else:
            await query.answer(
                "❌ Пока неверно. Попробуй ещё раз!",
                show_alert=True
            )

    elif action == "progress":
        data, user = get_user(query.from_user.id)

        lesson_number = min(user["lesson"] + 1, len(LESSONS))

        text = (
            "📊 ТВОЙ ПРОГРЕСС\n\n"
            f"🇨🇳 Урок: {lesson_number}/{len(LESSONS)}\n"
            f"⭐ XP: {user['xp']}\n"
            f"🔥 Серия: {user['streak']} день\n\n"
            "Продолжай заниматься каждый день! 💪"
        )

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "🏠 Главное меню",
                    callback_data="menu"
                )]
            ])
        )

    elif action == "repeat":
        data, user = get_user(query.from_user.id)
        lesson_index = min(user["lesson"], len(LESSONS) - 1)
        current = LESSONS[lesson_index]

        text = "🔁 ПОВТОРЕНИЕ\n\n"

        for word, pinyin, translation in current["words"]:
            text += f"🇨🇳 {word} — {pinyin} — {translation}\n"

        text += "\nПрочитай каждое слово вслух 3 раза. 🔊"

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "🧠 Пройти тест",
                    callback_data="quiz"
                )],
                [InlineKeyboardButton(
                    "🏠 Главное меню",
                    callback_data="menu"
                )]
            ])
        )


# =========================
# ЗАПУСК
# =========================

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Chinese bot started 🇨🇳")
    app.run_polling()


if __name__ == "__main__":
    main()    
