import os

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, URLInputFile
from aiogram.utils.chat_action import ChatActionSender

from common.db_api import change_balance, create_video_query
from common.enums import VideoModels
from common.models import User
from common.settings import settings
from tgbot_app.keyboards import gen_error_kb
from tgbot_app.utils.callbacks import VideoModelCallback
from tgbot_app.utils.generation_workers import run_video_generation
from tgbot_app.utils.misc import (can_send_query, delete_file,
                                  send_no_balance_msg, translate_text)
from tgbot_app.utils.states import VideoState
from tgbot_app.utils.text_variables import (CARTOON_VIDEO_TEXT,
                                            ERROR_MAIN_TEXT, IMG_TO_VIDEO_TEXT,
                                            RMBG_VIDEO_TEXT,
                                            TEXT_TO_VIDEO_TEXT,
                                            TRANSLATION_TEXT, VIDEO_GEN_TEXT)

router = Router()


@router.callback_query(VideoModelCallback.filter())
async def get_chapter_video(callback: CallbackQuery, callback_data: VideoModelCallback, state: FSMContext):
    await callback.answer()

    model = callback_data.model
    cost = settings.MODELS[model].cost

    match model:
        case VideoModels.TEXT_TO_VIDEO:
            text = TEXT_TO_VIDEO_TEXT
            await state.set_state(VideoState.TEXT_TO_VIDEO)
        case VideoModels.IMG_TO_VIDEO:
            text = IMG_TO_VIDEO_TEXT
            await state.set_state(VideoState.IMG_TO_VIDEO)
        case VideoModels.RMBG_VIDEO:
            text = RMBG_VIDEO_TEXT
            await state.set_state(VideoState.RMBG_VIDEO)
        case VideoModels.CARTOON_VIDEO:
            text = CARTOON_VIDEO_TEXT
            await state.set_state(VideoState.CARTOON_VIDEO)
        case _:
            return

    await callback.message.answer(text=text.format(cost=cost))


@router.message(VideoState.TEXT_TO_VIDEO)
async def run_text_to_video(message: Message, user: User):
    if not can_send_query(user=user, model=VideoModels.TEXT_TO_VIDEO):
        await send_no_balance_msg(user=user, bot=message.bot)

    status = await message.answer(TRANSLATION_TEXT)

    prompt = await translate_text(text=message.text, message=message)

    await status.edit_text(VIDEO_GEN_TEXT)

    result = await run_video_generation(model=VideoModels.TEXT_TO_VIDEO, prompt=prompt)

    await status.delete()

    if not result.success:
        await message.answer(text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
        return

    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id, action=ChatAction.UPLOAD_VIDEO):
        await message.answer_video(video=URLInputFile(url=result.result))
        await change_balance(user=user, model=settings.MODELS[VideoModels.TEXT_TO_VIDEO])
        await create_video_query(user_id=user.id, prompt=prompt, type=VideoModels.TEXT_TO_VIDEO, result=result.result)


@router.message(VideoState.IMG_TO_VIDEO)
async def run_img_to_video(message: Message, user: User):
    if not can_send_query(user=user, model=VideoModels.TEXT_TO_VIDEO):
        await send_no_balance_msg(user=user, bot=message.bot)

    if not message.photo:
        await message.answer("Мы не получили от Вас фото. Пожалуйста попробуйте ещё раз.")
        return

    if not message.caption:
        await message.answer("Вы должны прислать описание в комментарии к картинки. Попробуйте ещё раз.")
        return

    status = await message.answer(TRANSLATION_TEXT)

    prompt = await translate_text(text=message.caption, message=message)

    path_img = f"{settings.MEDIA_DIR}/tmp/{user.id}.png"

    await message.bot.download(file=message.photo[-1].file_id, destination=path_img)

    img_url = f"{settings.DOMAIN}/tmp/{user.id}.png"

    await status.edit_text(VIDEO_GEN_TEXT)

    result = await run_video_generation(model=VideoModels.IMG_TO_VIDEO, image=img_url, prompt=prompt)

    delete_file(path_img)

    await status.delete()

    if not result.success:
        await message.answer(text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
        return

    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id, action=ChatAction.UPLOAD_VIDEO):
        await message.answer_video(video=URLInputFile(url=result.result))
        await change_balance(user=user, model=settings.MODELS[VideoModels.IMG_TO_VIDEO])
        await create_video_query(user_id=user.id, prompt=f"{prompt} | {img_url}", type=VideoModels.IMG_TO_VIDEO,
                                 result=result.result)


@router.message(VideoState.CARTOON_VIDEO)
@router.message(VideoState.RMBG_VIDEO)
async def run_rmbg_cartoon_video(message: Message, user: User, state: FSMContext):
    if not can_send_query(user=user, model=VideoModels.TEXT_TO_VIDEO):
        await send_no_balance_msg(user=user, bot=message.bot)

    if not message.video:
        text = "Мы не получили от Вас видео. Пожалуйста попробуйте ещё раз."
        await message.answer(text=text)
        return

    if message.video.duration > 60:
        text = "Это видео слишком длинное. Оно не должно превышать 1 мин. Пожалуйста попробуйте ещё раз."
        await message.answer(text=text)
        return

    status = await message.answer(VIDEO_GEN_TEXT)

    video_path = f"{settings.MEDIA_DIR}/tmp/{user.id}.mp4"
    video_url = f"{settings.DOMAIN}/tmp/{user.id}.mp4"

    await message.bot.download(file=message.video.file_id, destination=video_path)

    cur_state = await state.get_state()

    if cur_state == VideoState.RMBG_VIDEO:
        model = VideoModels.RMBG_VIDEO
        result = await run_video_generation(model=model, input_video=video_url)
    else:
        model = VideoModels.CARTOON_VIDEO
        result = await run_video_generation(model=model, infile=video_url)

    delete_file(video_path)

    await status.delete()

    if not result or not result.success:
        await message.answer(text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
        return

    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id, action=ChatAction.UPLOAD_VIDEO):
        await change_balance(user=user, model=settings.MODELS[model])
        await create_video_query(user_id=user.id, prompt=video_url, type=model, result=result.result)
        await message.answer_video(video=URLInputFile(url=result.result))
