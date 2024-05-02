from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.db_api import get_roles
from common.enums import ImageModels, TextModels, VideoModels
from common.models import User
from common.settings import settings
from tgbot_app.utils.callbacks import (AiTypeCallback, ImageModelCallback,
                                       ProfileCallback, RoleCallback,
                                       TextModelCallback, TextSettingsCallback,
                                       VideoModelCallback, CommonCallback)
from tgbot_app.utils.enums import (AiTypeButtons, ProfileButtons,
                                   TextSettingsButtons, CommonChapter)


async def gen_ai_types_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for type_ in AiTypeButtons:
        builder.button(text=type_.value, callback_data=AiTypeCallback(type=type_))

    return builder.adjust(1).as_markup()


async def gen_txt_settings_kb(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Модель: " + settings.MODELS[user.txt_model].name,
        callback_data=TextSettingsCallback(action=TextSettingsButtons.MODEL)
    )

    builder.button(
        text="Синтез речи голос: " + (("✅ " + user.tts_mode) if user.tts_mode else "❌ Выключен"),
        callback_data=TextSettingsCallback(action=TextSettingsButtons.VOICE)
    )

    builder.button(
        text="Роль: " + (("✅ " + user.txt_model_role.title) if user.txt_model_role else "❌ Выключен"),
        callback_data=TextSettingsCallback(action=TextSettingsButtons.ROLE)
    )

    builder.button(
        text="Режим диалога: " + ("✅ Включен" if user.text_session_id else "❌ Выключен"),
        callback_data=TextSettingsCallback(action=TextSettingsButtons.CONTEXT)
    )

    builder.button(text="↩️ Назад", callback_data=CommonCallback(chapter=CommonChapter.AIS))

    return builder.adjust(1).as_markup()


async def gen_img_model_kb(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for model in ImageModels:  # type: ImageModels
        builder.button(
            text=("✅ " if user.img_model == model else "") + str(settings.MODELS[model].name),
            callback_data=ImageModelCallback(model=model)
        )

    builder.button(text="↩️ Назад", callback_data=CommonCallback(chapter=CommonChapter.AIS))

    return builder.adjust(1).as_markup()


async def gen_text_models_kb(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for model in TextModels:  # type: TextModels
        builder.button(
            text=("✅ " if user.txt_model == model else "") + str(settings.MODELS[model].name),
            callback_data=TextModelCallback(model=model)
        )

    builder.button(text="↩️ Назад", callback_data=TextSettingsCallback(action=TextSettingsButtons.BACK))

    return builder.adjust(1).as_markup()


async def gen_text_roles_kb(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    roles = await get_roles()
    sizes = []

    if user.txt_model_role:
        builder.button(text="❌ Отключить", callback_data=RoleCallback(role_id=0))
        sizes.append(1)

    for role in roles:
        builder.button(text=role.title, callback_data=RoleCallback(role_id=role.id))

    builder.button(text="↩️ Назад", callback_data=TextSettingsCallback(action=TextSettingsButtons.BACK))

    sizes += [2 for _ in range(len(roles) // 2)] + [1]

    return builder.adjust(*sizes).as_markup()


async def gen_main_video_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for model in VideoModels:  # type: VideoModels
        builder.button(text=settings.MODELS[model].name, callback_data=VideoModelCallback(model=model))

    builder.button(text="↩️ Назад", callback_data=CommonCallback(chapter=CommonChapter.AIS))

    builder.adjust(1)

    return builder.as_markup()
