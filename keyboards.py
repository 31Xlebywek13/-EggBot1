from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🥚 Профиль"),
             KeyboardButton(text="🏆 Топ вибраций")],
            [KeyboardButton(text="💛 Пожертвовать вибрации"),
             KeyboardButton(text="🧘 Медитация")],
            [KeyboardButton(text="🎁 Получить бонус")]
        ],
        resize_keyboard=True
    )

def justice_keyboard(case_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🕊 Помиловать",
                callback_data=f"justice_pardon_{case_id}"
            ),
            InlineKeyboardButton(
                text="☠️ Казнить",
                callback_data=f"justice_execute_{case_id}"
            )
        ]]
    )
