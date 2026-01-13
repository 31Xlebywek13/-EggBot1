from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import ADMINS
from database import set_rank, add_vibrations

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


@router.message(lambda m: m.text and m.text.startswith("/setrank"))
async def setrank(message: Message):
    if not is_admin(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответь на сообщение пользователя.")
        return

    # /setrank <ранг...>
    rank = message.text.replace("/setrank", "", 1).strip()
    if not rank:
        await message.answer("Напиши ранг после команды.")
        return

    user_id = message.reply_to_message.from_user.id
    set_rank(user_id, rank)

    await message.reply_to_message.reply(f"🏅 Тебе присвоен ранг: {rank}")


@router.message(Command("adminhelp"))
async def admin_help(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "👑 *Админ-панель Верховного Яйца*\n\n"
        "⭐ *Оценка сообщений*\n"
        "/rate — (ответом) начислить +5 вибраций\n\n"
        "⚖ *Суд Яйца*\n"
        "/justice — начать суд (ответом)\n"
        "/verdict — вынести приговор (ответом на сообщение суда)\n"
        "/pardon — обвиняемый может уменьшить голос за казнь\n\n"
        "🏅 *Ранги*\n"
        "/setrank <ранг> — назначить ранг (ответом)\n\n"
        "🛠 Прочее:\n"
        "Админы не участвуют в голосовании суда.\n"
        "Да направит Яйцо вашу волю.",
        parse_mode="Markdown"
    )

@router.message(Command("rate"))
async def rate(message: Message):
    if not is_admin(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("Ответь командой /rate на сообщение, которое хочешь оценить.")
        return

    target = message.reply_to_message.from_user
    if not target:
        await message.answer("Не удалось определить пользователя.")
        return

    add_vibrations(target.id, 5)
    await message.reply_to_message.reply("⭐ Верховному Яйцу понравился ваш комментарий.\n" "⚡ Вам начислено +5 вибраций!")
