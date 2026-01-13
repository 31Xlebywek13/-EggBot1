from aiogram import Router
from aiogram.types import Message

from database import donate, get_profile

router = Router()

# временное хранилище состояний (простое)
waiting_donation = set()


@router.message(lambda m: m.text == "💛 Пожертвовать вибрации")
async def ask_amount(message: Message):
    waiting_donation.add(message.from_user.id)

    await message.answer(
        "🥚 Сколько вибраций ты готов отдать Яйцу?\n"
        "Напиши число."
    )


@router.message(lambda m: m.from_user.id in waiting_donation and m.text and m.text.isdigit())
async def donate_amount(message: Message):
    user_id = message.from_user.id
    amount = int(message.text)

    user = get_profile(user_id)

    if not user:
        waiting_donation.discard(user_id)
        return

    balance = user["vibrations"]

    if amount <= 0:
        await message.answer("🥚 Сумма должна быть больше нуля.")
        return

    if amount > balance:
        await message.answer("🥚 У тебя недостаточно вибраций.")
        return

    donate(user_id, amount, anonymous=False)
    waiting_donation.discard(user_id)

    await message.answer(
        f"💛 Ты пожертвовал {amount} вибраций Верховному Яйцу.\n"
        f"Баланс вселенной стабилизирован."
    )
