from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from lexicon.ru_ru import *
from keyboards.keyboards import *

USER = Router()


@USER.message(CommandStart())
async def start(message: Message):
    await message.answer(START, reply_markup=StaticKeyboards.MENU_KEYBOARDS)