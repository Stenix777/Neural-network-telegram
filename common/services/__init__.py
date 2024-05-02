from common.services.neiro_api import AsyncNeiroAPI
from common.services.robokassa import Robokassa
from common.settings import settings

robokassa = Robokassa(login=settings.ROBOKASSA_LOGIN, password_1=settings.ROBOKASSA_PASS1,
                      password_2=settings.ROBOKASSA_PASS2)
neiro_api = AsyncNeiroAPI(token=settings.NEIRO_TOKEN)
