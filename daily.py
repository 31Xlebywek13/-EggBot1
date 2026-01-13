from aiogram import Router
from aiogram.types import Message
from datetime import date, timedelta
from database import get_user, add_vibrations, cur, conn

router = Router()


@router.message(lambda m: m.text == "/daily")
async def daily(message: Message):
    user = get_user(message.from_user.id)

    today = date.today()
    last = user["last_daily"]

    if last == today.isoformat():
        await message.answer("🎁 Ты уже получил ежедневную награду сегодня.")
        return

    # streak
    streak = user["daily_streak"]
    if last:
        last_date = date.fromisoformat(last)
        if last_date == today - timedelta(days=1):
            streak += 1
        else:
            streak = 1
    else:
        streak = 1

    reward = 5 + streak  # растёт каждый день

    add_vibrations(user["user_id"], reward)

    cur.execute("""
        UPDATE users SET last_daily=?, daily_streak=? WHERE user_id=?
    """, (today.isoformat(), streak, user["user_id"]))
    conn.commit()

    await message.answer(
        f"🎁 Ежедневная награда: {reward} вибраций!\n"
        f"🔥 Стрик: {streak} дней подряд"
    )
@router.message(lambda m: m.text == "🎁 Получить бонус")
async def daily_button(message: Message):
    await daily(message)
