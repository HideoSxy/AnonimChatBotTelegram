from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from typing import ClassVar


async def menu_commands(bot: Bot, chat_id: int) -> None:
    scope = BotCommandScopeChat(chat_id=chat_id)
    await bot.set_my_commands([
        BotCommand(command='/menu', description='Главное меню')
    ], scope=scope)


async def room_commands(bot: Bot, chat_id: int) -> None:
    scope = BotCommandScopeChat(chat_id=chat_id)
    await bot.set_my_commands([
        BotCommand(command='/exit', description='Покинуть комнату')
    ], scope=scope)

class StaticKeyboards:
    MENU_KEYBOARDS: ClassVar[InlineKeyboardMarkup] = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Выбрать никнейм', callback_data='NICK'), InlineKeyboardButton(text='Создать комнату', callback_data='CRTROOM')],
        [InlineKeyboardButton(text='Выбрать комнату', callback_data='CHROOM')]
    ])

    CANCEL: ClassVar[InlineKeyboardMarkup] = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data='CANCEL')]
    ])


class DynamicKeyboards:
    @staticmethod
    def choose_rooms(rooms: list, page: int, amount: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for id, name, capacity, available in rooms:
            kb.button(
                text=f'{name} | {capacity - available}/{capacity}',
                callback_data=str(id)
            )
        kb.adjust(1)
        kb.row(InlineKeyboardButton(text='<', callback_data='PREV'),
               InlineKeyboardButton(text=f'{page + 1}/{amount}', callback_data='STAT'),
               InlineKeyboardButton(text='>', callback_data='NEXT'))
        return kb.as_markup()