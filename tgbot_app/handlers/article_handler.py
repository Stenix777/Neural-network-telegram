import json

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, URLInputFile

from common.db_api import change_balance, create_service_query
from common.enums import ServiceModels
from common.models import User
from common.settings import settings
from tgbot_app.keyboards import (gen_article_mode_kb, gen_article_search_kb,
                                 gen_edit_work_plan_kb, gen_error_kb,
                                 gen_services_back_kb)
from tgbot_app.utils.callbacks import ArticleCallback, WorkingCallback
from tgbot_app.utils.enums import (ArticleAction, ArticleModes, WorkingButtons,
                                   WorkPlanButtons)
from tgbot_app.utils.generation_workers import run_service_generation
from tgbot_app.utils.misc import send_no_balance_msg
from tgbot_app.utils.states import ArticleState
from tgbot_app.utils.text_variables import (ARTICLE_AUTO_TEXT,
                                            ARTICLE_CONFIRM_PLAN_TEXT,
                                            ARTICLE_EDIT_PLAN_TEXT,
                                            ARTICLE_ENGINE_TEXT,
                                            ARTICLE_ERROR_PLAN_TEXT,
                                            ARTICLE_PLAN_PROCESS_TEXT,
                                            ARTICLE_PRO_TEXT, ARTICLE_TEXT,
                                            ERROR_MAIN_TEXT, PROGRESS_TEXT)

router = Router()


@router.callback_query(WorkingCallback.filter(F.type == WorkingButtons.ARTICLE))
async def article_handler(callback: CallbackQuery):
    await callback.message.answer(text=ARTICLE_TEXT.format(cost=settings.MODELS[ServiceModels.ARTICLE].cost),
                                  reply_markup=await gen_article_mode_kb())
    await callback.answer()


@router.callback_query(ArticleCallback.filter(F.action == ArticleAction.MODE))
async def set_article_mode(callback: CallbackQuery, callback_data: ArticleCallback, state: FSMContext):
    mode = callback_data.value
    await callback.message.answer(text=ARTICLE_AUTO_TEXT if mode == ArticleModes.AUTO else ARTICLE_PRO_TEXT)
    await callback.answer()

    await state.set_state(ArticleState.START)
    await state.set_data({"mode": mode})


@router.message(ArticleState.START)
async def set_article_theme(message: Message, user: User, state: FSMContext):
    if user.token_balance < settings.MODELS[ServiceModels.ARTICLE].cost:
        await state.clear()
        await send_no_balance_msg(user=user, bot=message.bot)

    data = await state.get_data()
    mode = data.get("mode")

    if mode == ArticleModes.EXPERT:
        await state.update_data({"search_query": message.text})
        await message.answer(text=ARTICLE_ENGINE_TEXT, reply_markup=await gen_article_search_kb())
        return

    status = await message.answer(PROGRESS_TEXT.format(progress="1%"))

    result = await run_service_generation(model=ServiceModels.ARTICLE, status=status, theme=message.text)

    await status.delete()

    if not result.success:
        await message.answer(text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
        return

    await message.answer_document(
        document=URLInputFile(result.result, filename=f"{message.text.replace(' ', '_')}.html"))

    await create_service_query(user_id=user.id, type=ServiceModels.ARTICLE, result=result.result)
    await change_balance(user=user, model=settings.MODELS[ServiceModels.ARTICLE])


@router.callback_query(ArticleCallback.filter(F.action == ArticleAction.ENGINE))
async def set_search_engine_article(callback: CallbackQuery, callback_data: ArticleCallback, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    search_query = data.get("search_query")
    engine = callback_data.value

    status = await callback.message.answer(ARTICLE_PLAN_PROCESS_TEXT)

    result = await run_service_generation(model=ServiceModels.ARTICLE_PLAN, search_query=search_query,
                                          engine=engine.value)

    if not result.success:
        await callback.message.answer(text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
        return

    result = json.loads(result.result)

    await state.update_data({"work_plan": result})

    work_plan_str = "\n".join([f"{num}. {chapter}" for num, chapter in enumerate(result, start=1)])

    await status.edit_text(text=ARTICLE_CONFIRM_PLAN_TEXT.format(work_plan=work_plan_str),
                           reply_markup=await gen_edit_work_plan_kb())


@router.callback_query(ArticleCallback.filter(F.value == WorkPlanButtons.EDIT))
async def edit_work_plan(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(ARTICLE_EDIT_PLAN_TEXT)
    await callback.answer()

    await state.set_state(ArticleState.EDIT_PLAN)


@router.message(ArticleState.EDIT_PLAN)
async def confirm_work_plan(message: Message, state: FSMContext):
    user_work_plan = [chapter for chapter in message.text.split("\n") if chapter[0].isdigit()]

    if not user_work_plan:
        text = ARTICLE_ERROR_PLAN_TEXT
        markup = await gen_services_back_kb()
    else:
        text = "\n".join(user_work_plan)
        markup = await gen_edit_work_plan_kb()

        await state.update_data({"work_plan": user_work_plan})

    await message.answer(text=text, reply_markup=markup)


@router.callback_query(ArticleCallback.filter(F.value == WorkPlanButtons.RUN))
async def start_expert_generation(callback: CallbackQuery, user: User, state: FSMContext):
    await callback.answer()

    if user.token_balance < settings.MODELS[ServiceModels.ARTICLE].cost:
        await state.clear()
        await send_no_balance_msg(user=user, bot=callback.message.bot)

    data = await state.get_data()
    work_plan = data.get("work_plan")
    search_query = data.get("search_query")

    status = await callback.message.answer(PROGRESS_TEXT.format(progress="1%"))

    result = await run_service_generation(model=ServiceModels.ARTICLE, status=status, theme=search_query,
                                          plan=work_plan)

    await status.delete()

    if not result.success:
        await callback.message.answer(text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
        return

    await callback.message.answer_document(
        document=URLInputFile(result.result, filename=f"{search_query.replace(' ', '_')}.html"))

    await create_service_query(user_id=user.id, type=ServiceModels.ARTICLE, result=result.result)
    await change_balance(user=user, model=settings.MODELS[ServiceModels.ARTICLE])
    await state.clear()
