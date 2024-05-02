from aiogram.fsm.state import State, StatesGroup


class GenerationState(StatesGroup):
    TEXT = State()
    IMAGE = State()
    FILE = State()
    IN_PROCESS = State()


class VideoState(StatesGroup):
    TEXT_TO_VIDEO = State()
    IMG_TO_VIDEO = State()
    RMBG_VIDEO = State()
    CARTOON_VIDEO = State()
    PICA = State()


class DiplomaState(StatesGroup):
    TYPE_WORK = State()
    THEME_WORK = State()
    STRUCT_WORK = State()


class CommonState(StatesGroup):
    REWRITE = State()
    VISION = State()
    STT = State()
    TTS = State()
    LINK = State()


class ArticleState(StatesGroup):
    START = State()
    EDIT_PLAN = State()
