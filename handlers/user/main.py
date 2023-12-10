from io import BytesIO
import datetime

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType
from aiogram import html
from aiogram.utils.markdown import html as md_html

from keyboards.inline import language_kb
from keyboards.reply import get_menu_kb, get_type_meter_kb, REMOVE_KB
from db.models.user import UserStore
from db.models.user_profile import UserProfileStore
from utils.states import RegState, MeterReadingsState, ProfileState
from utils.get_file import get_file
from utils.defaults import type_of_meter
from google.googleAPI import upload_file_to_user_folder
from utils.language import _
from db.get_locale import get_locale



async def start(message: Message):
    # init user in db
    user_id = message.from_user.id
    data = {"user_id": user_id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name}
    user = await UserStore.create_user(data)
    await message.answer(_("Hello, {name}!", 'en').format(
        name=html.quote(message.from_user.full_name)
    ), reply_markup=language_kb)


async def reg_profile_step1(message: Message, state: FSMContext):
    await state.set_state(RegState.send_account_id)
    await state.update_data(address=message.text)
    user_id = message.from_user.id
    await message.answer(_("Send your account_id", await get_locale(user_id)))


async def reg_profile_step2(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    data = {
        "user_id": user_id,
        "address": data["address"],
        "account_id": message.text,
    }
    new_profile = await UserProfileStore.create_user_profile(data)
    locale = await get_locale(user_id)
    await message.answer(_("Profile setup, go to menu", locale), reply_markup=get_menu_kb(locale),
                         )

    await state.clear()


async def menu(message: Message):
    user_id = message.from_user.id
    locale = await get_locale(user_id)
    kb = get_menu_kb(locale)
    await message.answer(_("Choose option:", locale), reply_markup=kb)


async def meter_reading_init(message: Message, state: FSMContext):
    user_id = message.from_user.id
    locale = await get_locale(user_id)
    await message.answer(_("Choose type of meter:", locale), reply_markup=get_type_meter_kb(locale))
    await state.set_state(MeterReadingsState.choose_type)


async def meter_reading_type(message: Message, state: FSMContext):
    type_ = message.text
    user_id = message.from_user.id
    locale = await get_locale(user_id)
    if type_ not in type_of_meter:
        await message.answer(_("Choose type by buttons", locale))
    await state.update_data(type_=type_)

    await message.answer(_("Send photo of meter.", locale), reply_markup=REMOVE_KB)

    await state.set_state(MeterReadingsState.upload_photo)


async def meter_reading_photo_and_save(message: Message, state: FSMContext):
    user_id = message.from_user.id
    locale = await get_locale(user_id)
    user_data = await UserProfileStore.get_user_profile(user_id)
    data = await state.get_data()
    data_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    data_to_sheet = {
        "user_id": user_id,
        "account_id": user_data.account_id,
        "address": user_data.address,
        "meter_type": data["type_"],
        "photo_url": None,
        "created_at": data_time
    }

    file_id = message.photo[-1].file_id
    file_content = get_file(file_id)

    photo_stream = io.BytesIO(file_content)
    photo_stream.seek(0)

    upload_file_to_user_folder(photo_stream, user_id, data_to_sheet)

    await message.answer(_("Your data is saved.", locale))
    await message.answer(_("Choose:", locale), reply_markup=get_menu_kb(locale))
    await state.clear()


async def meter_photo_exception(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer(_("Should be photo, please send photo", await get_locale(user_id)))
    await state.set_state(MeterReadingsState.upload_photo)


async def profile_settings(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await UserStore.get_user_by_id(user_id)
    user_profile = await UserProfileStore.get_user_profile(user_id)
    username = user_data.username if not None else user_data.first_name
    account_id = user_profile.account_id
    address = user_profile.address
    bot: Bot = message.bot
    await message.answer(_("Welcome {name}!\n\n"
                           "Your account id: {account_id}\n"
                           "Your address: {address}\n\n"
                           "Choose data to change or back to menu:", await get_locale(user_id)).format(
        name=username,
        account_id=account_id,
        address=address
    ),
        reply_markup=get_profile_data_kb(user_data.language_code)
    )
    await state.set_state(ProfileState.choose_data_to_change)


async def profile_save_data(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    msg_to_edit = data["msg_id"]
    msg_to_delete = message.message_id
    type_ = data["type_"]
    data_to_update = message.text
    bot: Bot = message.bot
    new_data = {
        type_: data_to_update
    }
    await bot.delete_message(chat_id=user_id, message_id=msg_to_delete)

    if type_ == "account_id":
        update_user = await UserProfileStore.update_user_profile(user_id, new_data)
    elif type_ == "address":
        update_user = await UserProfileStore.update_user_profile(user_id, new_data)
    user_data = await UserStore.get_user_by_id(user_id)
    username = user_data.username if not None else user_data.first_name
    account_id = update_user.account_id
    address = update_user.address

    await bot.edit_message_text(
        text=_("Welcome {name}!\n\n"
               "Your account id: {account_id}\n"
               "Your address: {address}\n\n"
               "Choose data to change or back to menu:", await get_locale(user_id)).format(
            name=username,
            account_id=account_id,
            address=address
        ),
        chat_id=user_id,
        message_id=msg_to_edit,
        reply_markup=get_profile_data_kb(user_data.language_code),
        
    )
    await state.set_state(ProfileState.choose_data_to_change)


async def register_user_routers(router: Router):
    router.message.register(start, CommandStart())
    router.message.register(start, F.text == "Change Language")
    router.message.register(start, F.text == "Змінити мову")
    router.message.register(menu, Command(commands=['menu']), F.text == "Menu")
    router.message.register(menu, F.text == "Меню")
    router.message.register(reg_profile_step1, RegState.send_address)
    router.message.register(reg_profile_step2, RegState.send_account_id)
    router.message.register(meter_reading_init, F.text == "Send meter reading")
    router.message.register(meter_reading_init, F.text == "Надіслати показники лічильника")
    router.message.register(meter_reading_type, MeterReadingsState.choose_type)
    router.message.register(meter_reading_photo_and_save, MeterReadingsState.upload_photo, F.photo)
    router.message.register(meter_photo_exception, MeterReadingsState.upload_photo)
    router.message.register(profile_settings, F.text == "Profile")
    router.message.register(profile_settings, F.text == "Профіль")
    router.message.register(profile_save_data, ProfileState.save_data)
