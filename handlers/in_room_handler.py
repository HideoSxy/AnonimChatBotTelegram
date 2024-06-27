from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from lexicon.ru_ru import *
from keyboards.keyboards import *
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from database.dbcontroller import UsersTools, RoomsTools
from middlewares.outroom_filter_middleware import OutroomFilter
from handlers.user_handler import UserFSM

INROOM = Router()


@INROOM.message(Command(commands=['exit']))
async def exit_room(message: Message, state: FSMContext):
    UsersTools.free_room(message.from_user.id)
    await message.answer(EXIT_ROOM)
    await state.set_state(UserFSM.DEFAULT)
    await message.answer(START, reply_markup=StaticKeyboards.MENU_KEYBOARDS)
    await menu_commands(message.bot, message.chat.id)


@INROOM.message()
async def inroom_message(message: Message, state: FSMContext):
    for member in RoomsTools.get_room_members(UsersTools.get_room_id(message.from_user.id)):
        if member != message.from_user.id:
            nickname = UsersTools.get_nickname(message.from_user.id)
            try:
                await message.bot.send_message(
                    chat_id=member,
                    text=f'От: {nickname}\n\n'
                         f'{message.text}'
                )
            except TelegramBadRequest:
                ...