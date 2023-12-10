from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils import i18n
from aiogram.types import User

from db.models.user import UserStore
from db.models.user_profile import UserProfileStore
from db.get_locale import get_locale

from keyboards.reply import get_menu_kb
from keyboards.inline import get_profile_data_kb

from utils.language import _
from utils.states import RegState, ProfileState



async def cb_language_set(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    data = {
        "language_code": query.data
    }
    update = await UserStore.update_user(user_id=user_id, data=data)
    locale = await get_locale(user_id)
    await query.answer(_("Set new language", locale))
    bot: Bot = query.bot
    await bot.delete_message(chat_id=user_id, message_id=query.message.message_id)

    if await UserProfileStore.get_user_profile(user_id):
        await bot.send_message(chat_id=user_id,
                               text=_("Choose:", locale), reply_markup=get_menu_kb(locale))
        return None

    await bot.send_message(chat_id=user_id,
                           text=_("Configure profile, send your address", locale))
    await state.set_state(RegState.send_address)


async def profile_callback(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    l_code = await get_locale(user_id)
    bot: Bot = query.bot
    msg_id = query.message.message_id

    await state.update_data(msg_id=msg_id, type_=query.data)
    try:
        if query.data == "address":
            await bot.edit_message_text(chat_id=user_id, message_id=msg_id, reply_markup=get_profile_data_kb(l_code),
                                        text=_("Write your new address", l_code))
            await state.set_state(ProfileState.save_data)
        elif query.data == "account_id":
            await bot.edit_message_text(chat_id=user_id, message_id=msg_id, reply_markup=get_profile_data_kb(l_code),
                                        text=_("Write your new Account ID",l_code))
            await state.set_state(ProfileState.save_data)
        else:
            await bot.delete_message(chat_id=user_id, message_id=msg_id)
            await bot.send_message(chat_id=user_id, text=_("Choose:", l_code), reply_markup=get_menu_kb(l_code))
            await state.clear()
    except TelegramBadRequest:
        pass

def register_callback(router: Router):
    router.callback_query.register(cb_language_set, F.data == "uk")
    router.callback_query.register(cb_language_set, F.data == "en")
    router.callback_query.register(profile_callback, F.data == "address")
    router.callback_query.register(profile_callback, F.data == "account_id")
    router.callback_query.register(profile_callback, F.data == "go_to_menu")