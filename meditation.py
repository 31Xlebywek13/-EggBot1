from aiogram import Router
from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta
from database import get_user, add_vibrations, cur, conn
import random

router = Router()

MEDITATION_COOLDOWN = 2  # часы


# Кнопка в профиле
@router.callback_query(lambda c: c.data == "meditate_now")
async def meditate_button(call: CallbackQuery):
    user = get_user(call.from_user.id)

    now = datetime.utcnow()
    last = user["last_meditation"]

    if last:
        last = datetime.fromisoformat(last)
        diff = now - last

        if diff < timedelta(hours=MEDITATION_COOLDOWN):
            remain = timedelta(hours=MEDITATION_COOLDOWN) - diff
            hours = remain.seconds // 3600
            minutes = (remain.seconds % 3600) // 60

            await call.answer(
                f"Следующая медитация через {hours}ч {minutes}м",
                show_alert=True
            )
            return

# Кнопка в меню (если оставишь)
@router.message(lambda m: m.text == "🧘 Медитация")
async def meditate(message: Message):
    user = get_user(message.from_user.id)

    now = datetime.utcnow()
    last = user["last_meditation"]

    if last:
        last = datetime.fromisoformat(last)
        diff = now - last

        if diff < timedelta(hours=MEDITATION_COOLDOWN):
            remain = timedelta(hours=MEDITATION_COOLDOWN) - diff
            hours = remain.seconds // 3600
            minutes = (remain.seconds % 3600) // 60

            await message.answer(
                f"🧘 Ты уже медитировал.\n"
                f"Следующая медитация через {hours}ч {minutes}м."
            )
            return

    reward = random.randint(10, 20)

    items = (user["items"] or "").split(",")
    if "totem" in items and random.random() < 0.25:
        reward *= 2

    add_vibrations(user["user_id"], reward)

    cur.execute("UPDATE users SET last_meditation=? WHERE user_id=?",
                (now.isoformat(), user["user_id"]))
    conn.commit()

    next_time = timedelta(hours=MEDITATION_COOLDOWN)
    hours = next_time.seconds // 3600
    minutes = (next_time.seconds % 3600) // 60

    await message.answer(
        f"🧘 Ты медитировал и получил {reward} вибраций!\n"
        f"Следующая медитация через {hours}ч {minutes}м."
    )
