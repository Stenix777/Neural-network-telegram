from datetime import date, datetime, timedelta
from typing import Any

from loguru import logger
from sqlalchemy import desc, func, select

from common.enums import ImageModels, ServiceModels, TextModels, VideoModels
from common.models import (Invoice, ReferalLink, Report, Tariff,
                           TextGenerationRole, User, UserAdmin, db)
from common.models.generations import (ImageQuery, ServiceQuery, TextQuery,
                                       TextSession, VideoQuery)
from common.models.payments import Refund
from common.settings import Model, settings


async def get_or_create_user(tgid: int, username: str, first_name: str, last_name: str, link_id: str | None) -> User:
    async with db.async_session_factory() as session:
        user: User = await session.get(User, tgid)
        if link_id and link_id.isdigit():
            link: ReferalLink | None = await session.get(ReferalLink, int(link_id))
            link_id = int(link_id)
        else:
            link = link_id = None

        if not user:
            user = User(id=tgid, username=username if username else str(tgid), first_name=first_name,
                        last_name=last_name, referal_link_id=link_id)
            user.gemini_daily_limit = settings.FREE_GEMINI_QUERIES
            user.sd_daily_limit = settings.FREE_SD_QUERIES
            user.kandinsky_daily_limit = settings.FREE_KANDINSKY_QUERIES
            text_session = TextSession()
            user.text_session = text_session

            session.add(user)

            if link:
                link.new_users += 1
                link.clicks += 1

            logger.info(f"New user <{tgid}>")

        else:
            if not user.is_active:
                user.is_active = True
                user.gemini_daily_limit = settings.FREE_GEMINI_QUERIES
                user.kandinsky_daily_limit = settings.FREE_KANDINSKY_QUERIES
                user.sd_daily_limit = settings.FREE_SD_QUERIES
                user.update_daily_limits_time = datetime.now()
                session.add(user)

            if link and user.referal_link_id != link.id:
                link.clicks += 1

        if link:
            session.add(link)

        await session.commit()

        return user


async def get_obj_by_id(obj: Any, id_: int | str) -> Any:
    async with db.async_session_factory() as session:
        result = await session.get(obj, id_)
        return result


async def update_object(obj: Any, update_relations: bool = False, **params) -> None:
    async with db.async_session_factory() as session:
        for field, value in params.items():
            setattr(obj, field, value)
        session.add(obj)
        await session.commit()

        if update_relations:
            await session.refresh(obj)


async def get_roles() -> list[TextGenerationRole]:
    async with db.async_session_factory() as session:
        result = await session.scalars(
            select(TextGenerationRole).where(TextGenerationRole.is_active).order_by(TextGenerationRole.id)
        )

        return result.all()


async def switch_context(user: User) -> None:
    async with db.async_session_factory() as session:
        if not user.text_session_id:
            user.text_session = TextSession()
        else:
            await session.delete(user.text_session)
            user.text_session_id = None

        session.add(user)
        await session.commit()
        await session.refresh(user)


async def reset_session(user: User) -> None:
    if not user.text_session_id:
        return

    async with db.async_session_factory() as session:
        old_session = user.text_session
        user.text_session = TextSession(user=user)
        await session.delete(old_session)
        session.add(user)
        await session.commit()
        await session.refresh(user)


async def get_messages(session_id: int) -> list[TextQuery]:
    async with db.async_session_factory() as session:
        messages = await session.scalars(select(TextQuery).where(TextQuery.session_id == session_id))
        return messages.all()


async def create_text_query(user_id: int, session_id: int, prompt: str, result: str, model: TextModels) -> None:
    async with db.async_session_factory() as session:
        session.add(
            TextQuery(model=model, session_id=session_id, user_id=user_id, prompt=prompt, result=result)
        )
        await session.commit()


async def change_balance(user: User, model: Model, add: bool = False) -> None:  # TODO Review
    cost = model.cost if add else -model.cost

    if user.tariff:
        if model.name in ("ChatGPT 3.5 Turbo", "Kandinsky", "Gemini", "Stable Diffusion"):
            return
        user.token_balance += cost
    else:
        if model.name == "Gemini" and (user.gemini_daily_limit > 0 or (add and user.token_balance < model.cost)):
            user.gemini_daily_limit += 1 if add else -1
        elif model.name == "Kandinsky" and (user.kandinsky_daily_limit > 0 or (add and user.token_balance < model.cost)):
            user.kandinsky_daily_limit += 1 if add else -1
        elif model.name == "Stable Diffusion" and (user.sd_daily_limit > 0 or (add and user.token_balance < model.cost)):
            user.sd_daily_limit += 1 if add else -1
        else:
            user.token_balance += cost

    async with db.async_session_factory() as session:
        session.add(user)
        await session.commit()


async def create_image_query(**params) -> ImageQuery:
    query = ImageQuery(**params)
    async with db.async_session_factory() as session:
        session.add(query)
        await session.commit()

    return query


async def create_video_query(**params) -> VideoQuery:
    query = VideoQuery(**params)
    async with db.async_session_factory() as session:
        session.add(query)
        await session.commit()

    return query


async def create_service_query(**params) -> ServiceQuery:
    query = ServiceQuery(**params)
    async with db.async_session_factory() as session:
        session.add(query)
        await session.commit()

    return query


async def unsubscribe_user(user: User) -> None:
    user.tariff_id = None
    user.payment_tries = 0
    user.payment_time = None
    user.recurring = True
    user.txt_model = TextModels.GPT_3_TURBO
    user.img_model = ImageModels.STABLE_DIFFUSION
    user.tts_mode = ""
    user.check_subscriptions = True
    user.update_daily_limits_time = datetime.now()
    user.gemini_daily_limit = settings.FREE_GEMINI_QUERIES
    user.kandinsky_daily_limit = settings.FREE_KANDINSKY_QUERIES
    user.sd_daily_limit = settings.FREE_SD_QUERIES

    async with db.async_session_factory() as session:
        session.add(user)
        await session.commit()


async def get_tariffs(is_extra: bool = False, is_trial: bool = False) -> list[Tariff]:
    if is_trial:
        stmt = (select(Tariff)
                .where(Tariff.is_active, Tariff.is_extra == is_extra)
                .order_by("token_balance"))
    else:
        stmt = (select(Tariff)
                .where(Tariff.is_active, Tariff.is_extra == is_extra, ~Tariff.is_trial)
                .order_by("token_balance"))
    async with db.async_session_factory() as session:
        result = await session.scalars(stmt)
        return result.all()


async def get_last_invoice(user_id: int) -> Invoice | None:
    stmt = (select(Invoice)
            .where(Invoice.user_id == user_id, ~Invoice.tariff.has(Tariff.is_extra), Invoice.is_paid)
            .order_by(desc("created_at")))

    async with db.async_session_factory() as session:
        result = await session.scalars(stmt)
        return result.first()


async def create_refund(user: User) -> None:
    last_invoice = await get_last_invoice(user.id)

    stmt = (select(Invoice.id)
            .where(Invoice.user_id == user.id, Invoice.is_paid, Invoice.tariff.has(Tariff.is_extra),
                   Invoice.created_at.between(datetime.now(), last_invoice.created_at)))
    async with db.async_session_factory() as session:
        result = await session.execute(stmt)
        extra_invoices_cnt = result.raw.rowcount
        session.add(Refund(user_id=user.id, sum=last_invoice.tariff.price, attention=bool(result.raw.rowcount)))
        user.token_balance -= user.tariff.token_balance

        await session.commit()

    await unsubscribe_user(user)


def sync_get_object_by_id(obj: Any, id_: int) -> Any:
    with db.session_factory() as session:
        result = session.get(obj, id_)

        return result


def sync_create_obj(obj: Any, **params) -> Any:
    new_obj = obj(**params)
    with db.session_factory() as session:
        session.add(new_obj)
        session.commit()

    return new_obj


def sync_update_object(obj: Any, **params) -> None:
    with db.session_factory() as session:
        for field, value in params.items():
            setattr(obj, field, value)

        session.add(obj)
        session.commit()
        session.refresh(obj)
        session.close()


def update_subscription(user: User, invoice: Invoice) -> None:
    tariff: Tariff = invoice.tariff
    user.tariff = tariff

    if user.payment_time:  # Recurring update
        user.payment_time += timedelta(days=tariff.days)
    else:  # First payment
        user.payment_time = datetime.now() + timedelta(days=tariff.days)
        user.gemini_daily_limit = tariff.gemini_daily_limit
        user.kandinsky_daily_limit = tariff.kandinsky_daily_limit
        user.sd_daily_limit = tariff.sd_daily_limit
        user.check_subscriptions = False
        user.update_daily_limits_time = datetime.now() + timedelta(hours=24)

    user.token_balance += tariff.token_balance
    user.payment_tries = 0
    user.recurring = True
    user.first_payment = False

    if not user.mother_invoice_id:
        user.mother_invoice_id = invoice.id

    with db.session_factory() as session:
        session.add(user)
        session.commit()

    logger.info(f"SUBSCRIPTION UPDATED | User <{user.id}> | Tariff <{tariff.name}>")


def get_admin_user(username: str) -> UserAdmin:
    with db.session_factory() as session:
        result = session.scalar(select(UserAdmin).where(UserAdmin.username == username))
        return result


async def get_users_for_recurring() -> list[User]:
    async with db.async_session_factory() as session:
        result = await session.scalars(select(User).where(User.tariff_id.is_not(None),
                                                          User.payment_time.is_not(None),
                                                          User.mother_invoice_id.is_not(None),
                                                          User.payment_time < datetime.now()))
        return result.all()


async def create_invoice(**params) -> Invoice:
    invoice = Invoice(**params)

    async with db.async_session_factory() as session:
        session.add(invoice)
        await session.commit()
        await session.refresh(invoice)

    return invoice


async def get_admins_id() -> list[int]:
    async with db.async_session_factory() as session:
        result = await session.scalars(select(User.id).where(User.is_admin))

        return result.all()


async def get_users_id(premium: bool = False) -> list[int]:
    if premium:
        stmt = select(User.id).where(User.is_active, User.tariff_id.is_not(None))
    else:
        stmt = select(User.id).where(User.is_active, User.tariff_id.is_(None))

    async with db.async_session_factory() as session:
        result = await session.scalars(stmt)

    return result.all()


def sync_get_links(user_id: int) -> list[ReferalLink]:
    with db.session_factory() as session:
        return session.scalars(select(ReferalLink).where(ReferalLink.owner_id == user_id)).all()


async def create_object(obj: Any, **params) -> Any:
    new_obj = obj(**params)
    async with db.async_session_factory() as session:
        session.add(new_obj)
        await session.commit()

    return new_obj


async def create_report(auto: bool = False) -> Report:
    now = datetime.now()
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if auto:
        start_time = start_time - timedelta(hours=24)
        finish_time = start_time + timedelta(hours=24)
    else:
        finish_time = now
    time_range = [start_time, finish_time]

    logger.info(f"REPORT STARTED | {start_time} - {finish_time}")

    async with db.async_session_factory() as session:
        users_cnt = await session.scalar(select(func.count()).select_from(User))
        users_with_link_cnt = await session.scalar(select(func.count()).select_from(User).where(User.referal_link_id.is_not(None)))
        new_users_cnt = await session.scalar(select(func.count()).select_from(User).where(User.created_at.between(*time_range)))
        new_users_with_link_cnt = await session.scalar(select(func.count()).select_from(User).where(User.created_at.between(*time_range), User.referal_link_id.is_not(None)))
        _text_result = await session.execute(select(TextQuery.model, func.count()).select_from(TextQuery).where(TextQuery.created_at.between(*time_range)).group_by(TextQuery.model))
        _img_result = await session.execute(select(ImageQuery.model, func.count()).select_from(ImageQuery).where(ImageQuery.created_at.between(*time_range)).group_by(ImageQuery.model))
        _video_result = await session.execute(select(VideoQuery.type, func.count()).select_from(VideoQuery).where(VideoQuery.created_at.between(*time_range)).group_by(VideoQuery.type))
        _services_result = await session.execute(select(ServiceQuery.type, func.count()).select_from(ServiceQuery).where(ServiceQuery.created_at.between(*time_range)).group_by(ServiceQuery.type))
        text_queries_cnt = {model: count for model, count in _text_result}
        img_queries_cnt = {model: count for model, count in _img_result}
        video_queries_cnt = {model: count for model, count in _video_result}
        services_queries_cnt = {model: count for model, count in _services_result}
        prem_users_cnt = await session.scalar(select(func.count(User.id)).where(User.tariff_id.is_not(None)))
        new_prem_invoices_cnt = await session.scalar(select(func.count(Invoice.id)).where(Invoice.tariff.has(~Tariff.is_extra), Invoice.is_paid, Invoice.created_at.between(*time_range)))
        new_prem_invoices_sum = await session.scalar(select(func.sum(Invoice.sum)).where(Invoice.tariff.has(~Tariff.is_extra), Invoice.is_paid, Invoice.created_at.between(*time_range)))
        new_token_invoices_cnt = await session.scalar(select(func.count(Invoice.id)).where(Invoice.tariff.has(Tariff.is_extra), Invoice.is_paid, Invoice.created_at.between(*time_range)))
        new_token_invoices_sum = await session.scalar(select(func.sum(Invoice.sum)).where(Invoice.tariff.has(Tariff.is_extra), Invoice.is_paid, Invoice.created_at.between(*time_range)))
        new_invoices_cnt = sum(i for i in [new_prem_invoices_cnt, new_token_invoices_cnt] if i is not None)
        new_invoices_sum = sum(i for i in [new_prem_invoices_sum, new_token_invoices_sum] if i is not None)
        avg_bill = int(new_invoices_sum / new_invoices_cnt) if new_invoices_cnt else 0
        trial_buys_cnt = await session.scalar(select(func.count()).select_from(Invoice).where(Invoice.tariff.has(Tariff.is_trial), Invoice.is_paid, Invoice.created_at.between(*time_range)))
        _tariffs_buys_result = await session.execute(select(Invoice.sum, func.count(Invoice.id)).where(Invoice.is_paid, Invoice.tariff.has(~Tariff.is_extra), Invoice.created_at.between(*time_range)).group_by(Invoice.sum))
        tariffs_buys_dict = {price: count for price, count in _tariffs_buys_result}
        recurring_invoices_cnt = await session.scalar(select(func.count()).select_from(Invoice).where(Invoice.mother_invoice_id.is_not(None), Invoice.created_at.between(*time_range), Invoice.is_paid))

        report = Report(
            users_cnt=users_cnt,
            users_with_link_cnt=users_with_link_cnt,
            new_users_cnt=new_users_cnt,
            new_users_with_link_cnt=new_users_with_link_cnt,
            new_users_from_search_cnt=new_users_cnt - new_users_with_link_cnt,
            queries_cnt=sum(count for count in (text_queries_cnt | video_queries_cnt | img_queries_cnt | services_queries_cnt).values()),
            queries_gpt_3_turbo_cnt=text_queries_cnt.get(TextModels.GPT_3_TURBO.value, 0),
            queries_gpt_4_turbo_cnt=text_queries_cnt.get(TextModels.GPT_4_TURBO.value, 0),
            queries_yagpt_cnt=text_queries_cnt.get(TextModels.YAGPT.value, 0),
            queries_yagpt_lite_cnt=text_queries_cnt.get(TextModels.YAGPT_LITE.value, 0),
            queries_gemini_cnt=text_queries_cnt.get(TextModels.GEMINI.value, 0),
            queries_claude_cnt=text_queries_cnt.get(TextModels.CLAUDE.value, 0),
            queries_sd_cnt=img_queries_cnt.get(ImageModels.STABLE_DIFFUSION.value, 0),
            queries_dalle_2_cnt=img_queries_cnt.get(ImageModels.DALLE_2.value, 0),
            queries_dalle_3_cnt=img_queries_cnt.get(ImageModels.DALLE_3.value, 0),
            queries_mj_cnt=img_queries_cnt.get(ImageModels.MIDJOURNEY.value, 0),
            queries_kandinsky_cnt=img_queries_cnt.get(ImageModels.KANDINSKY.value, 0),
            txt_to_video_cnt=video_queries_cnt.get(VideoModels.TEXT_TO_VIDEO.value, 0),
            img_to_video_cnt=video_queries_cnt.get(VideoModels.IMG_TO_VIDEO.value, 0),
            rembg_video_cnt=video_queries_cnt.get(VideoModels.RMBG_VIDEO.value, 0),
            cartoon_video_cnt=video_queries_cnt.get(VideoModels.CARTOON_VIDEO.value, 0),
            pica_video_cnt=0,  # TODO
            diploma_cnt=services_queries_cnt.get(ServiceModels.DIPLOMA.value, 0),
            rewrite_cnt=services_queries_cnt.get(ServiceModels.REWRITE.value, 0),
            vision_cnt=services_queries_cnt.get(ServiceModels.VISION.value, 0),
            articles_cnt=services_queries_cnt.get(ServiceModels.ARTICLE.value, 0),
            tts_cnt=services_queries_cnt.get(ServiceModels.TTS.value, 0),
            stt_cnt=services_queries_cnt.get(ServiceModels.STT.value, 0),
            rembg_cnt=0,  # TODO
            prem_users_cnt=prem_users_cnt,
            new_prem_invoices_cnt=new_prem_invoices_cnt,
            new_prem_invoices_sum=new_prem_invoices_sum if new_prem_invoices_sum is not None else 0,
            new_token_invoices_cnt=new_token_invoices_cnt,
            new_token_invoices_sum=new_token_invoices_sum if new_token_invoices_sum is not None else 0,
            new_invoices_cnt=new_invoices_cnt,
            new_invoices_sum=new_invoices_sum,
            avg_bill=avg_bill,
            trial_buys_cnt=trial_buys_cnt,
            tariffs_buys_dict=tariffs_buys_dict,
            recurring_invoices_cnt=recurring_invoices_cnt,
            date=date(year=start_time.year, month=start_time.month, day=start_time.day)
        )

        if auto:
            session.add(report)
            await session.commit()

    logger.info(f"REPORT FINISH")
    return report


def create_admin_user(username: str, password: str) -> None:
    with db.session_factory() as session:
        user = session.scalar(select(UserAdmin).where(UserAdmin.username == username))

        if not user:
            user = UserAdmin(username=username)

        user.set_password(password)
        session.add(user)
        session.commit()
