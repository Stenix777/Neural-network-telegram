from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot_app.keyboards import (gen_learning_kb, gen_other_services_kb,
                                 gen_services_kb, gen_working_kb)
from tgbot_app.utils.callbacks import ServicesCallback, CommonCallback
from tgbot_app.utils.enums import DefaultCommands, MainButtons, ServicesButtons, CommonChapter
from tgbot_app.utils.text_variables import (SERVICES_LEARNING_TEXT,
                                            SERVICES_MAIN_TEXT,
                                            SERVICES_OTHERS_TEXT,
                                            SERVICES_WORKING_TEXT)

router = Router()


@router.message(Command(DefaultCommands.services.name))
@router.message(F.text == MainButtons.SERVICES.value)
@router.callback_query(CommonCallback.filter(F.chapter == CommonChapter.SERVICES))
async def services(message: Message | CallbackQuery, state: FSMContext):
    await state.clear()

    if isinstance(message, CallbackQuery):
        await message.answer()
        message = message.message

    await message.answer(text=SERVICES_MAIN_TEXT, reply_markup=await gen_services_kb())


@router.callback_query(ServicesCallback.filter(F.type == ServicesButtons.LEARN))
async def choice_learning_service(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(text=SERVICES_LEARNING_TEXT, reply_markup=await gen_learning_kb())


@router.callback_query(ServicesCallback.filter(F.type == ServicesButtons.WORK))
async def choice_working_service(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(text=SERVICES_WORKING_TEXT, reply_markup=await gen_working_kb())


@router.callback_query(ServicesCallback.filter(F.type == ServicesButtons.OTHER))
async def choice_other_service(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(text=SERVICES_OTHERS_TEXT, reply_markup=await gen_other_services_kb())



