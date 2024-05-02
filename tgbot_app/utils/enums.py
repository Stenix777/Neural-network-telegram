from enum import Enum

from common.services.neiro_api import ResponseResult


class MainButtons(str, Enum):
    PROFILE = "⚡️ Тарифы и токены"
    AIS = "🤖 Нейросети"
    SERVICES = "📲 Сервисы"
    FAQ = "❓ Помощь"


class DefaultCommands(Enum):
    start = "Перезапуск 🚀"
    profile = "Профиль 👨‍💼"
    subscription = "Подписка 💳"
    tokens = "Токены 💎"
    ais = "Нейросети 🤖"
    services = "Сервисы 📲"
    faq = "Помощь ❓"


class ProfileButtons(Enum):
    PREMIUM = "💳 Премиум"
    TOKENS = "💎 Купить Токены"


class AiTypeButtons(Enum):
    TEXT = "🔤 Генерация текста"
    IMAGE = "🏞 Генерация изображений"
    VIDEO = "🎞 Генерация видео"
    MUSIC = "🎼 Генерация музыки"


class TextSettingsButtons(Enum):
    MODEL = "model"
    VOICE = "voice"
    ROLE = "role"
    CONTEXT = "context"
    BACK = "back"


class ServicesButtons(Enum):
    LEARN = "👨‍🎓 Для учёбы"
    WORK = "👨‍💻 Для работы"
    OTHER = "📱 Другие сервисы"


class LearningButtons(Enum):
    WORKS = "📄 Генерация работ"
    ANTIPLAGIARISM = "✍️ Повышение уникальности"
    PHOTO = "📸 Решение по фото"


class WorkingButtons(Enum):
    ARTICLE = "📰 Генерация статей"
    REWRITE = "✍️ Рерайт"


class OtherServicesButtons(Enum):
    TTS = "🔉 Текст в речь"
    STT = "🎤 Речь в текст"
    REMOVE_BACK = "🏙 Удаление фона"


class WorkTypes(Enum):
    ESSAY = "✏️ Эссе"
    DIPLOMA = "📚 Дипломная работа"
    COURSEWORK = "😮‍💨 Курсовая работа"
    REPORT = "📝 Реферат"


class DiplomaAction(Enum):
    SET_TYPE = "set_type"
    STRUCT = "struct"
    GET_STRUCT = "get_struct"
    CONFIRM = "confirm"
    START = "start"


class DiplomaStructButtons(Enum):
    START_GEN = "🪄 Начать генерацию"
    GET_STRUCT = "🗓 Задать план"


class SileroAction(Enum):
    SHOW_CATEGORY = "show_category"
    SHOW_CATEGORY_STATE = "show_category_state"
    SET = "set"
    EXAMPLE = "example"
    NONE = "none"
    BACK_TO_SERVICE = "back_to_service"
    SET_STATE = "set_state"
    START_SERVICE = "start_state"


class ArticleModes(Enum):
    AUTO = "Автоматический режим"
    EXPERT = "Режим эксперта"


class ArticleAction(Enum):
    MODE = "mode"
    ENGINE = "engine"
    WORK_PLAN = "work_plan"


class SearchEngine(Enum):
    GOOGLE = "google"
    YANDEX = "яндекс"


class WorkPlanButtons(Enum):
    EDIT = "Изменить структуру"
    RUN = "Продолжить генерацию"


class GenerationResult(ResponseResult):
    task_id: str | int | None = None


class FAQMainButtons(Enum):
    PREMIUM = "💳 Что дает премиум подписка?"
    TOKENS = "💎 Что такое токены?"
    RECOMMENDATIONS = "❗️ Рекомендации"
    PROBLEMS = "❌ Проблемы с ботом"
    INLINE = "➕ Как добавить бота в группу?"
    FINANCES = "💵 Финансовые вопросы"


class FAQRecButtons(Enum):
    USE = "Для чего можно использовать бот?"
    AIS = "Как правильно пользоваться нейросетями"
    WORK = "Генерация статей и учебных работ"


class FAQProblemsButtons(Enum):
    AI = "Не работает нейросеть"
    SERVICE = "Не работает сервис"


class FAQFinancesButtons(Enum):
    PREMIUM = "Не начислилась подписка"
    TOKENS = "Не начислились токены"
    RECURRING = "Продление подписки"
    REFUND = "Политика возврата средств"


class PaymentAction(Enum):
    SUBSCRIBE = "subscribe"
    CONFIRM = "confirm"
    REACTIVATE = "reactivate"
    CANCEL = "cancel"
    CONFIRM_CANCEL = "confirm_cancel"


class AdminMainButtons(Enum):
    LINKS = "🔗 Генерация ссылок"
    REPORT = "📈 Статистика бота"


class AdminLinksButtons(Enum):
    CREATE = "➕ Создать"


class CommonChapter(Enum):
    AIS = "ais"
    SERVICES = "services"
