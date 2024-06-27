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

USER = Router()

USER.message.middleware(OutroomFilter())


class UserFSM(StatesGroup):
    GETTING_NICKNAME: ClassVar[State] = State()
    GETTING_ROOM_NAME: ClassVar[State] = State()
    GETTING_ROOM_CAPACITY: ClassVar[State] = State()
    IN_ROOM: ClassVar[State] = State()
    DEFAULT: ClassVar[State] = State()


@USER.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(START, reply_markup=StaticKeyboards.MENU_KEYBOARDS)
    await state.set_state(UserFSM.DEFAULT)
    await menu_commands(message.bot, message.from_user.id)


@USER.message(Command(commands=['menu']))
async def menu(message: Message, state: FSMContext):
    await message.answer(MENU, reply_markup=StaticKeyboards.MENU_KEYBOARDS)
    await state.set_state(UserFSM.DEFAULT)
    RoomsTools.delete_deadrooms()


@USER.callback_query(F.data == 'CANCEL')
async def callback_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(MENU, reply_markup=StaticKeyboards.MENU_KEYBOARDS)
    await state.set_state(UserFSM.DEFAULT)


@USER.callback_query(F.data == 'NICK')
async def nickname_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    mes = await callback.message.edit_text(SET_NICK_TUTORIAL, reply_markup=StaticKeyboards.CANCEL)
    await state.set_state(UserFSM.GETTING_NICKNAME)
    await state.update_data(del_mes=mes.message_id)


@USER.message(StateFilter(UserFSM.GETTING_NICKNAME))
async def set_nick(message: Message, state: FSMContext):
    if len(message.text) > 25:
        await message.answer(NICKNAME_SET_ERROR)
        return None
    try:
        id_ = (await state.get_data())['del_mes']
        await message.chat.delete_message(id_)
    except TelegramBadRequest: # todo убрать дебагерские эксепты
        ...
    finally:
        await message.answer(NICKNAME_SET % (message.text,))
    UsersTools.set_nickname(message.from_user.id, message.text)
    await state.set_state(UserFSM.DEFAULT)


@USER.callback_query(F.data == 'CRTROOM')
async def create_room(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    msg = await callback.message.answer(SET_ROOM_NAME_TUTORIAL, reply_markup=StaticKeyboards.CANCEL)
    await state.update_data(del_mes=msg.message_id)
    await state.set_state(UserFSM.GETTING_ROOM_NAME)


@USER.message(StateFilter(UserFSM.GETTING_ROOM_NAME))
async def enter_room_name(message: Message, state: FSMContext):
    if len(message.text) > 25:
        await message.answer(ROOM_NAME_SET_ERROR)
        return None
    try:
        id_ = (await state.get_data())['del_mes']
        await message.chat.delete_message(id_)
    except TelegramBadRequest: # todo убрать дебагерские эксепты
        ...
    finally:
        msg = await message.answer(SET_ROOM_CAPACITY_TUTORIAL, reply_markup=StaticKeyboards.CANCEL)
    await state.update_data(room_name=message.text, del_mes=msg.message_id)
    await state.set_state(UserFSM.GETTING_ROOM_CAPACITY)


@USER.message(StateFilter(UserFSM.GETTING_ROOM_CAPACITY), F.text.isdigit())
async def enter_room_capacity(message: Message, state: FSMContext):
    if int(message.text) > 15:
        await message.answer(ROOM_CAPACITY_SET_ERR)
        return None
    room_name = (await state.get_data())['room_name']
    try:
        id_ = (await state.get_data())['del_mes']
        await message.chat.delete_message(id_)
    except TelegramBadRequest: # todo убрать дебагерские эксепты
        ...
    finally:
        await message.answer(ROOM_SET % (room_name, message.text))
    UsersTools.choose_room(message.from_user.id, RoomsTools.set_room(room_name, int(message.text)))
    await room_commands(message.bot, message.from_user.id)


@USER.callback_query(F.data == 'CHROOM')
async def choose_room(callback: CallbackQuery, state: FSMContext):
    rooms = RoomsTools.get_rooms()
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(CHOOSE_ROOM_TUTORIAL, reply_markup=DynamicKeyboards.choose_rooms(rooms[0], 0, len(rooms)))
    await state.update_data(rooms=rooms, page=0, amount=len(rooms))


@USER.callback_query(F.data.isdigit())
async def choosing_room(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    UsersTools.choose_room(callback.from_user.id, int(callback.data))
    await room_commands(callback.bot, callback.from_user.id)
    await state.set_state(UserFSM.IN_ROOM)
    await callback.message.answer(ROOM_CHOSEN % (callback.data,))


@USER.callback_query(F.data == 'NEXT')
async def next_page(callback: CallbackQuery, state: FSMContext):
    rooms = (await state.get_data())['rooms']
    page = (await state.get_data())['page']
    amount = (await state.get_data())['amount']
    if not(0 <= page + 1 <= amount - 1):
        await callback.answer("Максимальная страница", show_alert=True)
        return None
    await callback.message.edit_text(CHOOSE_ROOM_TUTORIAL, reply_markup=DynamicKeyboards.choose_rooms(rooms[page + 1], page=page + 1, amount=amount))
    await state.update_data(page=page + 1)
    await callback.answer()


@USER.callback_query(F.data == 'PREV')
async def previous_page(callback: CallbackQuery, state: FSMContext):
    rooms = (await state.get_data())['rooms']
    page = (await state.get_data())['page']
    amount = (await state.get_data())['amount']
    if not(0 <= page - 1 <= amount - 1):
        await callback.answer("Минимальная страница", show_alert=True)
        return None
    await callback.message.edit_text(CHOOSE_ROOM_TUTORIAL, reply_markup=DynamicKeyboards.choose_rooms(rooms[page + 1], page=page + 1, amount=amount))
    await state.update_data(page=page - 1)
    await callback.answer()







