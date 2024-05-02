import asyncio

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from common.db_api import create_image_query, update_object
from common.enums import ImageAction, ImageModels, ServiceModels, VideoModels
from common.models import ImageQuery
from common.services import neiro_api
from common.services.neiro_api import GenerationStatus
from tgbot_app.utils.enums import GenerationResult
from tgbot_app.utils.text_variables import IMAGE_GEN_TEXT, PROGRESS_TEXT


async def wait_image_result(model: ImageModels, task_id: str, status: Message, img_query: ImageQuery
                            ) -> GenerationResult:
    for _ in range(60):
        await asyncio.sleep(10)

        result = await neiro_api.get_status(task_id=task_id, model=model)

        if not result.success:
            continue

        if result.status in (GenerationStatus.ERROR, GenerationStatus.BANNED):
            await update_object(img_query, status=result.status)
            return GenerationResult(success=False, status=result.status)

        if result.status == GenerationStatus.WAITING:
            try:
                await status.edit_text("🕗 В ожидании начала генерации... Это может занять 3-5 минут...")
            except TelegramBadRequest:
                pass
            continue

        if result.status == GenerationStatus.IN_PROCESS:
            try:
                await status.edit_text(f"{IMAGE_GEN_TEXT} {result.result}")
            except TelegramBadRequest:
                pass
            continue

        if result.status == GenerationStatus.READY:
            result = result.result[0] if model == ImageModels.STABLE_DIFFUSION else result.result
            await update_object(img_query, status=GenerationStatus.READY, result=result)
            return GenerationResult(result=result, task_id=img_query.id)

    await update_object(img_query, status=GenerationStatus.ERROR, result='timeout')
    return GenerationResult(success=False)


async def run_mj_generation(action: ImageAction, status: Message, task_id: str = "", prompt: str = "",
                            index: int | None = None) -> GenerationResult:
    if action == ImageAction.IMAGINE:
        result = await neiro_api.imagine(model=ImageModels.MIDJOURNEY, prompt=prompt)
    else:
        result = await neiro_api.midjourney_action(action=action, index=index, task_id=task_id)

    if not result.success:
        return result

    cur_task_id = result.result

    img_query = await create_image_query(id=cur_task_id, user_id=status.chat.id, model=ImageModels.MIDJOURNEY,
                                         action=action, index=index, prompt=prompt)

    return await wait_image_result(model=ImageModels.MIDJOURNEY, task_id=cur_task_id, status=status,
                                   img_query=img_query)


async def run_image_generation(model: ImageModels, prompt: str, status: Message) -> GenerationResult:
    result = await neiro_api.imagine(model=model, prompt=prompt)

    if not result.success:
        return result

    await status.edit_text(IMAGE_GEN_TEXT)

    task_id = result.result

    img_query = await create_image_query(id=task_id, user_id=status.chat.id, model=model, action=ImageAction.IMAGINE,
                                         prompt=prompt)

    return await wait_image_result(model=model, task_id=task_id, status=status, img_query=img_query)


async def run_video_generation(model: VideoModels, **params) -> GenerationResult:
    result = await neiro_api.video_generation(model=model, params=params)

    if not result.success:
        return result

    task_id = result.result

    for _ in range(60):
        await asyncio.sleep(10)

        result = await neiro_api.get_status(task_id=task_id, model=ImageModels.STABLE_DIFFUSION)

        if not result.success:
            continue

        if result.status in (GenerationStatus.ERROR, GenerationStatus.BANNED):
            return GenerationResult(success=False, status=result.status)

        if result.status == GenerationStatus.READY:
            return GenerationResult(result=result.result[0])


async def run_service_generation(model: ServiceModels, status: Message = None, delay: int = 10, **params
                                 ) -> GenerationResult:
    result = await neiro_api.service_generation(model=model, params=params)

    if not result.success:
        return result

    task_id = result.result

    cur_result = "1%"

    for _ in range(180):
        await asyncio.sleep(delay)

        result = await neiro_api.get_status(task_id=task_id, model=model)

        if not result.success:
            continue

        if result.status == GenerationStatus.ERROR:
            return GenerationResult(success=False)

        if status and result.status == GenerationStatus.IN_PROCESS and result.result != cur_result:
            try:
                await status.edit_text(PROGRESS_TEXT.format(progress=result.result))
            except TelegramBadRequest:
                pass

            cur_result = result.result
            continue

        if result.status == GenerationStatus.READY:
            return GenerationResult(result=result.result)

    return GenerationResult(success=False)

