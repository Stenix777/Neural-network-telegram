from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.enums import ImageAction
from tgbot_app.utils.callbacks import MJCallback


async def gen_midjourney_kb(task_id: str):
    builder = InlineKeyboardBuilder()

    for action in (ImageAction.VARIATION, ImageAction.UPSAMPLE):
        for idx in range(1, 5):
            builder.button(
                text=f"{action[0].upper()}{idx}",
                callback_data=MJCallback(action=action, index=idx, task_id=task_id)
            )

    return builder.adjust(4, 4).as_markup()
