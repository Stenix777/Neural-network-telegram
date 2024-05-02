from aiogram.filters.callback_data import CallbackData

from common.enums import ImageAction, ImageModels, TextModels, VideoModels
from tgbot_app.utils.enums import (AdminLinksButtons, AdminMainButtons,
                                   AiTypeButtons, ArticleAction, ArticleModes,
                                   CommonChapter, DiplomaAction,
                                   FAQFinancesButtons, FAQMainButtons,
                                   FAQProblemsButtons, FAQRecButtons,
                                   LearningButtons, MainButtons,
                                   OtherServicesButtons, PaymentAction,
                                   ProfileButtons, SearchEngine,
                                   ServicesButtons, SileroAction,
                                   TextSettingsButtons, WorkingButtons,
                                   WorkPlanButtons)


class ProfileCallback(CallbackData, prefix="profile"):
    action: ProfileButtons


class AiTypeCallback(CallbackData, prefix="ai_type"):
    type: AiTypeButtons


class TextSettingsCallback(CallbackData, prefix="txt_settings"):
    action: TextSettingsButtons


class ImageModelCallback(CallbackData, prefix="img_model"):
    model: ImageModels


class TextModelCallback(CallbackData, prefix="txt_model"):
    model: TextModels


class VideoModelCallback(CallbackData, prefix="video_model"):
    model: VideoModels


class RoleCallback(CallbackData, prefix="txt_role"):
    role_id: int


class SileroCallback(CallbackData, prefix="silero"):
    action: SileroAction
    category: str = "0"
    subcategory: str = "0"
    value: str = "0"


class MJCallback(CallbackData, prefix="mj"):
    action: ImageAction
    index: int
    task_id: str


class ServicesCallback(CallbackData, prefix="services"):
    type: ServicesButtons


class LearningCallback(CallbackData, prefix="learning"):
    type: LearningButtons


class WorkingCallback(CallbackData, prefix="working"):
    type: WorkingButtons


class OtherServicesCallback(CallbackData, prefix="o_service"):
    type: OtherServicesButtons


class DiplomaCallback(CallbackData, prefix="diploma"):
    action: DiplomaAction
    value: str = "0"


class ArticleCallback(CallbackData, prefix="article"):
    action: ArticleAction
    value: ArticleModes | SearchEngine | WorkPlanButtons


class FAQCallback(CallbackData, prefix="faq"):
    chapter: FAQMainButtons | MainButtons | FAQRecButtons | FAQProblemsButtons | FAQFinancesButtons
    sub_chapter: str = "_"


class PaymentCallback(CallbackData, prefix="pay"):
    action: PaymentAction
    value: int | bool


class AdminCallback(CallbackData, prefix="admin"):
    chapter: AdminMainButtons


class AdminLinksCallback(CallbackData, prefix="adm_links"):
    command: AdminLinksButtons


class CommonCallback(CallbackData, prefix="common"):
    chapter: CommonChapter
