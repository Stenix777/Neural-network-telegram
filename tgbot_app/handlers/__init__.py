from aiogram import Router

from .admin_handler import router as admin_router
from .ais_handler import router as ais_router
from .article_handler import router as article_router
from .diploma_handler import router as diploma_router
from .empty_handler import router as empty_router
from .faq_handler import router as faq_router
from .gen_image_handler import router as image_router
from .gen_text_handler import router as text_router
from .gen_video_handler import router as video_router
from .modes_handler import router as modes_router
from .premium_handler import router as premium_router
from .profile_handler import router as profile_router
from .rewrite_handler import router as rewrite_router
from .services_handler import router as services_router
from .start_handlers import router as start_router
from .stt_handler import router as stt_router
from .tokens_handler import router as tokens_router
from .tts_handler import router as tts_router
from .vision_handler import router as vision_router

main_router = Router()

main_router.include_routers(
    start_router,
    ais_router,
    faq_router,
    profile_router,
    services_router,
    tokens_router,
    modes_router,
    diploma_router,
    rewrite_router,
    vision_router,
    article_router,
    stt_router,
    tts_router,
    premium_router,
    admin_router,
    image_router,
    text_router,
    video_router,
    empty_router,  # Mast be LAST!!!
)
