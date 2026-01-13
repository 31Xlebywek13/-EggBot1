from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database import add_vibrations, get_user

router = Router()


@router.message(Command("donate"))
async def donate(message: Message):
    # Проверяем, что команда написана ответом
    if not message.reply_to_message:
        await message.answer("💛 Ответьте командой /donate <число> на сообщение человека, которому хотите передать вибрации.")
        return

    # Проверяем аргументы
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("💛 Использование: /donate <число>")
        return

    amount = int(parts[1])
    if amount <= 0:
        await message.answer("💛 Сумма должна быть положительной.")
        return

    from_id = message.from_user.id
    to_id = message.reply_to_message.from_user.id

    if from_id == to_id:
        await message.answer("🥚 Нельзя передавать вибрации самому себе.")
        return

    donor = get_user(from_id)
    if donor["vibrations"] < amount:
        await message.answer("⚡ Недостаточно вибраций.")
        return

    # Переводим вибрации
    add_vibrations(from_id, -amount)
    add_vibrations(to_id, amount)

    username = message.reply_to_message.from_user.username or "пользователю"

    await message.answer(
        f"💛 Вы передали {amount} вибраций @{username}"
    )
