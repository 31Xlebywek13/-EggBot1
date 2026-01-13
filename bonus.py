from aiogram import Router
from aiogram.types import Message
from datetime import date

from database import add_vibrations

router = Router()

BONUS_AMOUNT = 10
daily_bonus = {}


@router.message(lambda m: m.text == "🎁 Бонус")
async def bonus(message: Message):
    user_id = message.from_user.id
    today = date.today()

    if daily_bonus.get(user_id) == today:
        await message.answer(
            "🎁 Бонус уже получен сегодня.\n"
            "⏳ Возвращайся завтра."
        )
        return

    daily_bonus[user_id] = today
    await add_vibrations(user_id, BONUS_AMOUNT)

    await message.answer(
        f"🎁 Верховное Яйцо благоволит тебе.\n"
        f"⚡ +{BONUS_AMOUNT} вибраций."
    )
