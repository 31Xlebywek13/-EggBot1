import asyncio
from datetime import datetime, time, timedelta

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, CHAT_ID
from database import init_db
from migrations import run_migrations

from handlers import (
    user,
    ritual,
    admin,
    justice,
    meditation,
    daily,
    donate,
)


async def daily_reminder(bot: Bot):
    """
    Ежедневное напоминание в чат в 10:00.
    """
    while True:
        now = datetime.now()
        target = datetime.combine(now.date(), time(10, 0))  # 10:00

        # если 10:00 уже прошло — переносим на завтра
        if now > target:
            target += timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        try:
            await bot.send_message(
                CHAT_ID,
                "🥚 Верховное Яйцо напоминает:\n"
                "💛 Сдайте вибрации, чтобы сохранить баланс вселенной."
            )
        except Exception as e:
            print("Ошибка отправки ежедневного сообщения:", e)

        # ждём сутки до следующего напоминания
        await asyncio.sleep(24 * 60 * 60)


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    init_db()
    run_migrations()
    
    # Подключаем роутеры
    dp.include_router(user.router)
    dp.include_router(ritual.router)
    dp.include_router(admin.router)
    dp.include_router(justice.router)
    dp.include_router(meditation.router)
    dp.include_router(daily.router)
    dp.include_router(donate.router)

    # Фоновая задача: ежедневное напоминание
    asyncio.create_task(daily_reminder(bot))

    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
