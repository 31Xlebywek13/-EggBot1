from aiogram import Router
from aiogram.types import Message, CallbackQuery

from config import ADMINS
from database import (
    create_case, add_vote,
    count_votes, get_case, close_case,
    get_user, remove_vibrations, cur, conn
)
from keyboards import justice_keyboard

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


# ============================
#   ЗАПУСК СУДА (ТОЛЬКО АДМИН)
# ============================

@router.message(lambda m: m.text == "/justice" and m.reply_to_message)
async def justice(message: Message):
    if not is_admin(message.from_user.id):
        return  # обычный игрок не может начать суд

    accused_id = message.reply_to_message.from_user.id

    case_id = create_case(
        message.chat.id,
        message.reply_to_message.message_id,
        accused_id
    )

    await message.reply_to_message.reply(
        "⚖️ Суд Верховного Яйца начался!",
        reply_markup=justice_keyboard(case_id)
    )


# ============================
#   ГОЛОСОВАНИЕ
# ============================

@router.callback_query(lambda c: c.data and c.data.startswith("justice_"))
async def vote(call: CallbackQuery):
    parts = call.data.split("_")
    if len(parts) != 3:
        await call.answer("Некорректные данные.", show_alert=True)
        return

    _, vote_choice, case_id_str = parts

    try:
        case_id = int(case_id_str)
    except:
        await call.answer("Некорректный ID дела.", show_alert=True)
        return

    case = get_case(case_id)
    if not case:
        await call.answer("⚖️ Дело уже закрыто.", show_alert=True)
        return

    accused_id = case["accused_id"]

    # Обвиняемый НЕ может голосовать
    if call.from_user.id == accused_id:
        await call.answer("🥚 Обвиняемый не голосует.", show_alert=True)
        return

    # Админы НЕ голосуют
    if is_admin(call.from_user.id):
        await call.answer("🥚 Админы не участвуют в голосовании.", show_alert=True)
        return

    add_vote(case_id, call.from_user.id, vote_choice)

    await call.answer("🥚 Голос учтён")


# ============================
#   ПОМИЛОВАНИЕ (ТОЛЬКО ОБВИНЯЕМЫЙ)
# ============================

@router.message(lambda m: m.text == "/pardon" and m.reply_to_message)
async def pardon(message: Message):
    user = get_user(message.from_user.id)

    rm = message.reply_to_message.reply_markup
    if not rm or not rm.inline_keyboard:
        await message.answer("🥚 Это не сообщение суда.")
        return

    try:
        case_id = int(rm.inline_keyboard[0][0].callback_data.split("_")[-1])
    except:
        await message.answer("🥚 Не удалось определить дело.")
        return

    case = get_case(case_id)
    if not case:
        await message.answer("⚖️ Дело уже закрыто.")
        return

    # Проверяем, что это обвиняемый
    if case["accused_id"] != message.from_user.id:
        await message.answer("🕊 Только обвиняемый может уменьшать голоса.")
        return

    cost = 30
    if user["vibrations"] < cost:
        await message.answer("⚡ Недостаточно вибраций.")
        return

    # Уменьшаем один голос "execute"
    cur.execute("""
        UPDATE votes SET vote='pardon'
        WHERE case_id=? AND vote='execute'
        LIMIT 1
    """, (case_id,))
    conn.commit()

    remove_vibrations(user["user_id"], cost)

    await message.answer("🕊 Ты уменьшил один голос за казнь!")


# ============================
#   ПРИГОВОР (ТОЛЬКО АДМИН)
# ============================

@router.message(lambda m: m.text == "/verdict" and m.reply_to_message)
async def verdict(message: Message):
    if not is_admin(message.from_user.id):
        return  # обычный игрок не может вынести приговор

    rm = message.reply_to_message.reply_markup
    if not rm or not rm.inline_keyboard:
        await message.answer("🥚 Это не сообщение суда.")
        return

    try:
        case_id = int(rm.inline_keyboard[0][0].callback_data.split("_")[-1])
    except:
        await message.answer("🥚 Не удалось определить дело.")
        return

    case = get_case(case_id)
    if not case:
        await message.answer("🥚 Это дело уже закрыто.")
        return

    votes = count_votes(case_id)
    pardon = votes.get("pardon", 0)
    execute = votes.get("execute", 0)

    chat_id = case["chat_id"]
    accused = case["accused_id"]

    if execute > pardon:
        try:
            await message.bot.ban_chat_member(chat_id, accused)
            result = "☠️ КАЗНЬ"
        except:
            result = "☠️ КАЗНЬ (не удалось забанить)"
    else:
        result = "🕊 ПОМИЛОВАНИЕ"

    close_case(case_id)

    await message.answer(
        f"⚖️ Приговор Яйца:\n"
        f"{result}\n\n"
        f"🕊 {pardon} | ☠️ {execute}"
    )
