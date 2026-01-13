from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database import get_profile, add_user, top_donators
from keyboards import main_keyboard

router = Router()


@router.message(Command("start"), F.chat.type == "private")
async def start(message: Message):
    add_user(message.from_user.id, message.from_user.username)
    await message.answer("🥚 Верховное Яйцо наблюдает", reply_markup=main_keyboard())


@router.message(lambda m: m.text == "🥚 Профиль")
async def profile(message: Message):
    user = get_profile(message.from_user.id)

    await message.answer(
        f"👑 Ранг: {user['rank']}\n"
        f"⚡ Вибрации: {user['vibrations']}\n"
        f"💛 Пожертвовано: {user['donated']}\n"
        f"⚖ Участий в судах: {user['court_votes']}\n"
        f"🎁 Стрик: {user['daily_streak']} дней\n"
    )


@router.message(lambda m: m.text == "🏆 Топ вибраций")
async def top(message: Message):
    top_list = top_donators()
    if not top_list:
        await message.answer("🏆 Пока нет жертвователей.")
        return

    text = "🏆 ТОП ЖЕРТВОВАТЕЛЕЙ:\n\n"
    for i, u in enumerate(top_list, 1):
        username = u["username"] or "безымянный"
        text += f"{i}. @{username} — {u['donated']}\n"

    await message.answer(text)


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "<b>Помощь культа Яйца</b>\n\n"
        "⚖ <b>Суд:</b>\n"
        "/pardon — судимый за цену в 30 вибраций может убрать 1 голос за казнь (работает 1 раз)\n\n"
        "🪓 <b>Казнь:</b>\n"
        "Удаление из канала/чата\n\n"
        "💛 <b>Донат:</b>\n"
        "/donate число — ответьте командой на сообщение человека, которому хотите передать вибрации\n\n"
        "🎁 <b>Бонус:</b>\n"
        "Доступен кнопкой в боте и командой /daily\n\n"
        "👑 <b>Ранги:</b>\n"
        "🥚 Послушник\n"
        "🕯 Посвящённый\n"
        "🛡 Хранитель\n"
        "⚔️ Страж Равновесия\n"
        "👑🥚 Верховный Посланник Яйца\n"
        "<i>Ранги пока ничего не дают, но в будущем у них будет применение. "
        "Выдаются админами за активность.</i>\n\n"
        "🐞 Сообщить о багах/ошибках, вопросы/предложения — @xlebywek_buwka",
        parse_mode="HTML"
    )
