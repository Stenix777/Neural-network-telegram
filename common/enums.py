from enum import Enum


class TextModels(str, Enum):
    GPT_3_TURBO = "gpt-3.5-turbo-1106"
    GPT_4_TURBO = "gpt-4-1106-preview"
    CLAUDE = "claude-2.1"
    GEMINI = "gemini-1.0-pro"
    YAGPT = "yandexgpt"
    YAGPT_LITE = "yandexgpt-lite"


class ImageModels(str, Enum):
    MIDJOURNEY = "midjourney"
    STABLE_DIFFUSION = "sd"
    DALLE_2 = "dall-e-2"
    DALLE_3 = "dall-e-3"
    KANDINSKY = "kandinsky"


class VideoModels(str, Enum):
    TEXT_TO_VIDEO = "text2mpeg"
    IMG_TO_VIDEO = "img2mpeg"
    RMBG_VIDEO = "rembg"
    CARTOON_VIDEO = "mpeg2cartoon"


class ServiceModels(str, Enum):
    DIPLOMA = "diploma"
    STT = "speech-to-text"
    TTS = "text-to-speech"
    REWRITE = "rewrite"
    VISION = "vision"
    ARTICLE = "article-generate"
    ARTICLE_PLAN = "article-plan"


class ImageAction(str, Enum):
    IMAGINE = "imagine"
    VARIATION = "variation"
    UPSAMPLE = "upsample"
