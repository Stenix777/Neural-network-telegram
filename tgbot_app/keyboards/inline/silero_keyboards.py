from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot_app.utils.callbacks import (ServicesCallback, SileroCallback,
                                       TextSettingsCallback)
from tgbot_app.utils.enums import (ServicesButtons, SileroAction,
                                   TextSettingsButtons)
from tgbot_app.utils.silero_speakers import SPEAKERS


async def gen_tts_kb(cur_speaker: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    text = "Голос: " + (cur_speaker if cur_speaker else "Не выбран")

    builder.button(text=text, callback_data=SileroCallback(action=SileroAction.START_SERVICE))
    builder.button(text="↩️ Назад", callback_data=ServicesCallback(type=ServicesButtons.OTHER))

    return builder.adjust(1).as_markup()


async def gen_main_speaker_kb(cur_speaker: str | None, is_service: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    sizes = []

    if cur_speaker:
        builder.button(text="Выключить", callback_data=SileroCallback(action=SileroAction.SET))
        sizes.append(1)

    for main_set in SPEAKERS.keys():
        builder.button(
            text=main_set,
            callback_data=SileroCallback(
                action=SileroAction.SHOW_CATEGORY_STATE if is_service else SileroAction.SHOW_CATEGORY,
                category=main_set,
            ),
        )

    if is_service:
        builder.button(text="↩️ Назад", callback_data=SileroCallback(action=SileroAction.BACK_TO_SERVICE))
    else:
        builder.button(text="↩️ Назад", callback_data=TextSettingsCallback(action=TextSettingsButtons.BACK))

    sizes += [1, 1, 1] + [2 for _ in range((len(SPEAKERS) - 3) // 2)] + [1]

    return builder.adjust(*sizes).as_markup()


async def gen_speaker_category_kb(
        cur_speaker: str, category: str, cur_subcategory: str = "0", is_service: bool = False) -> InlineKeyboardMarkup:
    speakers = SPEAKERS[category]
    builder = InlineKeyboardBuilder()
    sizes = [1]

    if isinstance(speakers, dict):
        builder.button(text="Выберите набор голосов 👇", callback_data=SileroCallback(action=SileroAction.NONE))

        for subcategory in speakers.keys():
            if cur_subcategory == "0":
                cur_subcategory = subcategory

            text = f"✅ {subcategory}" if cur_subcategory == subcategory else subcategory
            builder.button(
                text=text,
                callback_data=SileroCallback(
                    action=SileroAction.SHOW_CATEGORY_STATE if is_service else SileroAction.SHOW_CATEGORY,
                    category=category,
                    subcategory=subcategory,
                ),
            )

        sizes += [2 for _ in range(len(speakers) // 2)] + [1, 1]

        speakers = speakers[cur_subcategory]

    builder.button(text="Выберите голос героя 👇", callback_data=SileroCallback(action=SileroAction.NONE))

    for speaker in speakers:
        text = f"✅ {speaker}" if cur_speaker == speaker else speaker

        builder.button(
            text=text,
            callback_data=SileroCallback(
                action=SileroAction.SET_STATE if is_service else SileroAction.SET,
                category=category,
                subcategory=cur_subcategory,
                value=speaker,
            ),
        )

    sizes += [2 for _ in range(len(speakers) // 2)] + [1]

    if cur_speaker:
        builder.button(text="Отправить пример", callback_data=SileroCallback(action=SileroAction.EXAMPLE))

    if is_service:
        builder.button(text="↩️ Назад", callback_data=SileroCallback(action=SileroAction.BACK_TO_SERVICE))
    else:
        builder.button(text="↩️ Назад", callback_data=TextSettingsCallback(action=TextSettingsButtons.BACK))

    return builder.adjust(*sizes).as_markup()
