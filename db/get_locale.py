from .models.user import UserStore


async def get_locale(user_id):
    data = await UserStore.get_user_language_code(user_id)
    return data
