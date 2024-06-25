from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot
from typing import ClassVar

async def build_commands(bot: Bot) -> None:
    ...


class StaticKeyboards:
    MENU_KEYBOARDS: ClassVar[InlineKeyboardMarkup] = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Выбрать никнейм', callback_data='NICK'), InlineKeyboardButton(text='Создать комнату', callback_data='CRTROOM')],
        [InlineKeyboardButton(text='Выбрать комнату', callback_data='CHROOM')]
    ])

