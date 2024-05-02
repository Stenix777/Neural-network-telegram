from datetime import date

from sqlalchemy import Date, JSON
from sqlalchemy.orm import Mapped, mapped_column

from common.models import Base


class Report(Base):
    __tablename__ = "reports"

    users_cnt: Mapped[int] = mapped_column(name="Всего пользователей", default=0)
    users_with_link_cnt: Mapped[int] = mapped_column(name="Пользователей с реф. ссылок", default=0)
    new_users_cnt: Mapped[int] = mapped_column(name="Новых пользователей", default=0)
    new_users_with_link_cnt: Mapped[int] = mapped_column(name="Новых пользователей с реф. ссылок", default=0)
    new_users_from_search_cnt: Mapped[int] = mapped_column(name="Новых пользователей с поиска", default=0)
    queries_cnt: Mapped[int] = mapped_column(name="Кол-во запросов", default=0)
    queries_gpt_3_turbo_cnt: Mapped[int] = mapped_column(name="Кол-во запросов ChatGPT 3", default=0)
    queries_gpt_4_turbo_cnt: Mapped[int] = mapped_column(name="Кол-во запросов ChatGPT 4", default=0)
    queries_yagpt_cnt: Mapped[int] = mapped_column(name="Кол-во запросов YaGPT", default=0)
    queries_yagpt_lite_cnt: Mapped[int] = mapped_column(name="Кол-во запросов YaGPT Lite", default=0)
    queries_gemini_cnt: Mapped[int] = mapped_column(name="Кол-во запросов Gemini", default=0)
    queries_claude_cnt: Mapped[int] = mapped_column(name="Кол-во запросов Claude", default=0)
    queries_sd_cnt: Mapped[int] = mapped_column(name="Кол-во запросов StableDiffusion", default=0)
    queries_dalle_2_cnt: Mapped[int] = mapped_column(name="Кол-во запросов DALL-E-2", default=0)
    queries_dalle_3_cnt: Mapped[int] = mapped_column(name="Кол-во запросов DALL-E-3", default=0)
    queries_mj_cnt: Mapped[int] = mapped_column(name="Кол-во запросов Midjourney", default=0)
    queries_kandinsky_cnt: Mapped[int] = mapped_column(name="Кол-во запросов Kandinsky", default=0)
    txt_to_video_cnt: Mapped[int] = mapped_column(name="Кол-во генераций текст в видео", default=0)
    img_to_video_cnt: Mapped[int] = mapped_column(name="Кол-во генераций картинка в видео", default=0)
    rembg_video_cnt: Mapped[int] = mapped_column(name="Кол-во удаления фона с видео", default=0)
    cartoon_video_cnt: Mapped[int] = mapped_column(name="Кол-во генераций видео в мульт", default=0)
    pica_video_cnt: Mapped[int] = mapped_column(name="Кол-во генераций PicaArt", default=0)
    diploma_cnt: Mapped[int] = mapped_column(name="Кол-во генераций дипломов", default=0)
    rewrite_cnt: Mapped[int] = mapped_column(name="Кол-во рерайта", default=0)
    vision_cnt: Mapped[int] = mapped_column(name="Кол-во решений по фото", default=0)
    articles_cnt: Mapped[int] = mapped_column(name="Кол-во генераций статей", default=0)
    tts_cnt: Mapped[int] = mapped_column(name="Кол-во озвучек", default=0)
    stt_cnt: Mapped[int] = mapped_column(name="Кол-во речь в текст", default=0)
    rembg_cnt: Mapped[int] = mapped_column(name="Кол-во удаления фона с картинок", default=0)
    prem_users_cnt: Mapped[int] = mapped_column(name="Кол-во премиум пользователей", default=0)
    new_prem_invoices_cnt: Mapped[int] = mapped_column(name="Кол-во новых оплат премиума", default=0)
    new_prem_invoices_sum: Mapped[int] = mapped_column(name="Сумма новых оплат премиума", default=0)
    new_token_invoices_cnt: Mapped[int] = mapped_column(name="Кол-во новых оплат токенов", default=0)
    new_token_invoices_sum: Mapped[int] = mapped_column(name="Сумма новых оплат токенов", default=0)
    new_invoices_cnt: Mapped[int] = mapped_column(name="Кол-во новых оплат", default=0)
    new_invoices_sum: Mapped[int] = mapped_column(name="Сумма новых оплат", default=0)
    avg_bill: Mapped[int] = mapped_column(name="Средний чек", default=0)
    trial_buys_cnt: Mapped[int] = mapped_column(name="Кол-во покупок триала", default=0)
    tariffs_buys_dict: Mapped[dict] = mapped_column(JSON, name="Кол-во покупок по тарифам", default=0)
    recurring_invoices_cnt: Mapped[int] = mapped_column(name="Кол-во продлений", default=0)
    date: Mapped[date] = mapped_column(Date, name="Дата")

    def __str__(self):
        return self.date

    def __repr__(self):
        return f"<Report: {self.date}>"

