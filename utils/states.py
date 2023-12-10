from aiogram.fsm.state import State, StatesGroup


class RegState(StatesGroup):
    send_address = State()
    send_account_id = State()


class MeterReadingsState(StatesGroup):
    choose_type = State()
    upload_photo = State()


class ProfileState(StatesGroup):
    choose_data_to_change = State()
    save_data = State()

